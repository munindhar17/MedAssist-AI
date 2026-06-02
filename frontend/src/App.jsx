import "./App.css"
import { useEffect, useMemo, useState } from "react"
import axios from "axios"
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import SpeechRecognition, {
  useSpeechRecognition,
} from "react-speech-recognition"

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"

const symptomAliases = {
  "heart pain": "chest pain",
  "cardiac pain": "chest pain",
  "high sugar": "increased appetite",
  "sugar problem": "increased appetite",
  "stomach ache": "stomach pain",
  "belly pain": "stomach pain",
  "shortness of breath": "breathlessness",
  "difficulty breathing": "breathlessness",
  "rapid heartbeat": "fast heart rate",
  "heart racing": "fast heart rate",
  "painful urination": "burning micturition",
  "burning urination": "burning micturition",
  "burning urine": "burning micturition",
  "black head": "blackheads",
  "black heads": "blackheads",
}

const relatedSymptomMap = {
  headache: ["nausea", "blurred_and_distorted_vision", "dizziness"],
  chest_pain: ["breathlessness", "fast_heart_rate", "sweating"],
  dizziness: ["loss_of_balance", "fatigue"],
  cough: ["high_fever", "phlegm", "breathlessness"],
  burning_micturition: ["continuous_feel_of_urine", "bladder_discomfort"],
  blackheads: ["pus_filled_pimples", "skin_rash"],
}

const riskClass = (risk = "Low") => `risk${risk}`

const confidenceColor = (percent = 0) => {
  if (percent >= 70) {
    return "linear-gradient(90deg, #34d399, #059669)"
  }
  if (percent >= 40) {
    return "linear-gradient(90deg, #fde68a, #f59e0b)"
  }
  return "linear-gradient(90deg, #fecdd3, #ef4444)"
}

const formatSymptom = (value = "") => value.replaceAll("_", " ")

const formatSymptomList = (value = "") =>
  String(value)
    .split(",")
    .map((item) => formatSymptom(item).trim())
    .filter(Boolean)
    .join(", ")

const MEDICAL_DISCLAIMER =
  "This application is for educational purposes only and does not provide medical diagnosis, treatment, or emergency care recommendations."

const toSymptomKey = (value = "") =>
  value.toLowerCase().replace(/[^\w\s]/g, "").trim().replaceAll(" ", "_")

const truncateLabel = (label = "", maxLength = 10) =>
  label.length > maxLength ? `${label.slice(0, maxLength)}...` : label

const EmptyState = ({ icon = "i", title, message }) => (
  <div className="emptyState">
    <div className="emptyIcon" aria-hidden="true">{icon}</div>
    <strong>{title}</strong>
    {message && <p>{message}</p>}
  </div>
)

const SeverityTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null

  const item = payload[0].payload

  return (
    <div className="chartTooltip">
      <strong>{item.fullLabel}</strong>
      <span>Severity {item.severity}</span>
    </div>
  )
}

const HighlightedSymptom = ({ label, query }) => {
  const safeQuery = query.trim()
  if (!safeQuery) return label

  const matchIndex = label.toLowerCase().indexOf(safeQuery.toLowerCase())
  if (matchIndex === -1) return label

  return (
    <>
      {label.slice(0, matchIndex)}
      <mark>{label.slice(matchIndex, matchIndex + safeQuery.length)}</mark>
      {label.slice(matchIndex + safeQuery.length)}
    </>
  )
}

const normalizeSpokenText = (value = "") => {
  let normalized = value.toLowerCase().replace(/[^\w\s]/g, " ")

  Object.entries(symptomAliases).forEach(([alias, symptom]) => {
    const pattern = new RegExp(`\\b${alias}\\b`, "gi")
    normalized = normalized.replace(pattern, symptom)
  })

  return normalized.replace(/\s+/g, " ").trim()
}

function App() {
  const [allSymptoms, setAllSymptoms] = useState([])
  const [search, setSearch] = useState("")
  const [selectedSymptoms, setSelectedSymptoms] = useState([])
  const [invalidSymptoms, setInvalidSymptoms] = useState([])
  const [result, setResult] = useState(null)
  const [history, setHistory] = useState([])
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(false)
  const [analyticsLoading, setAnalyticsLoading] = useState(false)
  const [showEmergency, setShowEmergency] = useState(false)
  const [question, setQuestion] = useState("")
  const [chatReply, setChatReply] = useState("")
  const [suggestedSymptoms, setSuggestedSymptoms] = useState([])
  const [nearbyDoctors, setNearbyDoctors] = useState([])
  const [nearbyLoading, setNearbyLoading] = useState(false)
  const [nearbySearched, setNearbySearched] = useState(false)
  const [voiceProcessing, setVoiceProcessing] = useState(false)
  const [locationError, setLocationError] = useState("")
  const [profileApplied, setProfileApplied] = useState(false)

  const hasPredictions = result?.predictions?.length > 0
  const hasValidPrediction = result?.has_prediction === true
  const topPrediction = hasValidPrediction ? result.predictions[0] : null
  const topConfidence = topPrediction ? parseFloat(topPrediction.confidence) : 0
  const confidenceLabel = topConfidence >= 70
    ? "High confidence diagnosis"
    : topConfidence >= 40
      ? "Moderate confidence prediction"
      : "Low confidence prediction"

  const [profile, setProfile] = useState({
    name: "",
    age: "",
    gender: "",
    height: "",
    weight: "",
    conditions: "",
    allergies: "",
  })

  const {
    transcript,
    listening,
    resetTranscript,
  } = useSpeechRecognition()

  const normalizeSymptomKey = (value = "") =>
    value.toLowerCase().replace(/[^\w\s]/g, "").trim().replaceAll(" ", "_")

  const isGenderInvalidSymptom = (symptom) => {
    return (
      profile.gender?.toLowerCase?.() === "male" &&
      normalizeSymptomKey(symptom) === "abnormal_menstruation"
    )
  }

  const addSymptom = (symptom) => {
    const normalized = normalizeSymptomKey(symptom)

    if (isGenderInvalidSymptom(normalized)) {
      setInvalidSymptoms((prev) => (
        prev.includes(normalized) ? prev : [...prev, normalized]
      ))
      setSelectedSymptoms((prev) => prev.filter((item) => item !== normalized))
      return
    }

    setInvalidSymptoms((prev) => prev.filter((item) => item !== normalized))
    setSelectedSymptoms((prev) => (
      prev.includes(normalized) ? prev : [...prev, normalized]
    ))
  }

  const remove = (item) => {
    setSelectedSymptoms((prev) => prev.filter((symptom) => symptom !== item))
    setInvalidSymptoms((prev) => prev.filter((symptom) => symptom !== item))
  }

  const loadHistory = async () => {
    try {
      const res = await axios.get(`${API}/history`)
      setHistory(res.data.history || [])
    } catch (err) {
      console.log(err)
    }
  }

  const loadAnalytics = async () => {
    setAnalyticsLoading(true)
    try {
      const res = await axios.get(`${API}/analytics`)
      setAnalytics(res.data)
    } catch (err) {
      console.log(err)
    } finally {
      setAnalyticsLoading(false)
    }
  }

  const loadProfile = () => {
    const saved = localStorage.getItem("healthProfile")
    if (saved) {
      const parsed = JSON.parse(saved)
      setProfile(parsed)
      setProfileApplied(true)
    }
  }

  useEffect(() => {
    const initialize = async () => {
      try {
        const res = await axios.get(`${API}/symptoms`)
        setAllSymptoms(res.data.symptoms || [])
        loadProfile()
        await loadHistory()
        await loadAnalytics()
      } catch (err) {
        console.log(err)
      }
    }

    initialize()
  }, [])

  const filteredSymptoms = useMemo(() => {
    const query = search.toLowerCase().trim()
    if (!query) return []

    return allSymptoms
      .filter((item) => {
        const label = formatSymptom(item).toLowerCase()
        const aliasMatch = Object.entries(symptomAliases).some(
          ([alias, symptom]) =>
            symptom === label && alias.includes(query)
        )

        return (
          (label.includes(query) || aliasMatch) &&
          !selectedSymptoms.includes(item)
        )
      })
      .slice(0, 7)
  }, [allSymptoms, search, selectedSymptoms])

  const trendData = useMemo(() => (
    (analytics?.severity_trend?.length ? analytics.severity_trend.slice(-10) : history.slice(0, 10).reverse())
      .map((item) => ({
        label: truncateLabel(item.time, 14),
        fullLabel: item.time,
        severity: item.severity,
      }))
  ), [analytics, history])

  useEffect(() => {
    if (!transcript) return

    const lower = normalizeSpokenText(transcript)
    const matched = []

    allSymptoms.forEach((symptom) => {
      const label = formatSymptom(symptom).toLowerCase()
      if (lower.includes(label)) {
        matched.push(symptom)
      }
    })

    Object.values(symptomAliases).forEach((symptom) => {
      const key = toSymptomKey(symptom)
      if (lower.includes(symptom) && allSymptoms.includes(key)) {
        matched.push(key)
      }
    })

    matched.forEach(addSymptom)
  }, [transcript, allSymptoms])

  const startVoice = () => {
    resetTranscript()
    setVoiceProcessing(true)
    setResult(null)
    SpeechRecognition.startListening({
      continuous: false,
      language: "en-US",
    })

    setTimeout(() => {
      SpeechRecognition.stopListening()
      setVoiceProcessing(false)
    }, 4000)
  }

  const stopVoice = () => {
    SpeechRecognition.stopListening()
    setVoiceProcessing(false)
  }

  const clearAll = () => {
    setSelectedSymptoms([])
    setSuggestedSymptoms([])
    resetTranscript()
    setResult(null)
  }

  const saveProfile = () => {
    localStorage.setItem("healthProfile", JSON.stringify(profile))
    setProfileApplied(true)
  }

  const predict = async () => {
    if (selectedSymptoms.length === 0 || loading) return

    setLoading(true)

    try {
      const res = await axios.post(`${API}/predict`, {
        symptoms: selectedSymptoms,
        profile: {
          name: profile.name || undefined,
          age: profile.age ? Number(profile.age) : undefined,
          gender: profile.gender || undefined,
          height: profile.height ? Number(profile.height) : undefined,
          weight: profile.weight ? Number(profile.weight) : undefined,
          conditions: profile.conditions
            ? profile.conditions.split(",").map((item) => item.trim()).filter(Boolean)
            : [],
          allergies: profile.allergies
            ? profile.allergies.split(",").map((item) => item.trim()).filter(Boolean)
            : [],
        },
      })

      setResult(res.data)
      setNearbyDoctors([])
      setNearbySearched(false)
      setLocationError("")

      const apiSuggestions = res.data.suggested_symptoms || []
      const nextSuggestions = apiSuggestions.filter((item) => !selectedSymptoms.includes(item))

      setSuggestedSymptoms([...new Set(nextSuggestions)].slice(0, 4))

      if (res.data.emergency?.emergency) {
        setShowEmergency(true)
      }

      await loadHistory()
      await loadAnalytics()
    } catch (err) {
      console.log(err)
    } finally {
      setLoading(false)
    }
  }

  const findNearbyDoctors = () => {
    setLocationError("")
    setNearbyDoctors([])
    setNearbySearched(false)

    if (!result) {
      setLocationError("No prediction available to search nearby doctors.")
      return
    }

    if (!navigator.geolocation) {
      setLocationError("Geolocation is not supported by your browser.")
      return
    }

    setNearbyLoading(true)

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords
        try {
          const res = await axios.get(`${API}/nearby-doctors`, {
            params: {
              latitude,
              longitude,
              specialty: result.recommended_doctor || "General Physician",
            },
          })
          setNearbyDoctors(res.data || [])
          setNearbySearched(true)
        } catch (err) {
          console.log(err)
          setLocationError("Unable to fetch nearby doctors.")
          setNearbySearched(true)
        } finally {
          setNearbyLoading(false)
        }
      },
      (error) => {
        console.log(error)
        setLocationError("Location permission denied or unavailable.")
        setNearbySearched(true)
        setNearbyLoading(false)
      }
    )
  }

  const askAI = async () => {
    if (!question.trim()) return

    try {
      const res = await axios.post(`${API}/chat`, { question })
      setChatReply(res.data.reply)
    } catch (err) {
      console.log(err)
    }
  }

  return (
    <div className="app">
      {showEmergency && result?.emergency && (
        <div className="emergencyOverlay">
          <div className="emergencyModal">
            <h2>Emergency Alert</h2>
            <p>{result.emergency.message}</p>
            {result.emergency.symptoms.length > 0 && (
              <div>
                <strong>Symptoms:</strong>
                <ul>
                  {result.emergency.symptoms.map((item) => (
                    <li key={item}>{formatSymptom(item)}</li>
                  ))}
                </ul>
              </div>
            )}
            <button className="closeBtn" onClick={() => setShowEmergency(false)}>
              Close
            </button>
          </div>
        </div>
      )}

      <main className="wrap">
        <section className="hero">
          <div className="pill">AI Health Assistant</div>
          <h1 className="title">
            Medical prediction
            <br />
            <em>intelligently designed</em>
          </h1>
          <p className="subtitle">AI Diagnosis - Smart Prediction - Health Insights</p>
        </section>

        <section className="glass">
          <div className="searchWrap">
            <input
              className="search"
              placeholder="Search symptoms..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && filteredSymptoms.length > 0) {
                  addSymptom(filteredSymptoms[0])
                  setSearch("")
                }
              }}
            />
            {filteredSymptoms.length > 0 && (
              <div className="suggestions">
                {filteredSymptoms.map((item) => (
                  <button
                    key={item}
                    type="button"
                    className="suggestionItem"
                    onClick={() => {
                      addSymptom(item)
                      setSearch("")
                    }}
                  >
                    <HighlightedSymptom label={formatSymptom(item)} query={search} />
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="voiceButtons">
            <button className="voiceStart" onClick={startVoice} disabled={voiceProcessing}>
              {voiceProcessing ? "Processing..." : "Start Voice"}
            </button>
            <button className="voiceStop" onClick={stopVoice} disabled={!listening && !voiceProcessing}>
              Stop
            </button>
            <button className="voiceClear" onClick={clearAll}>
              Clear
            </button>
          </div>

          {listening && <p className="voiceStatus">Listening...</p>}
          {transcript && <p className="voiceText">Voice: {transcript}</p>}

          <div className="chips">
            {selectedSymptoms.length > 0 || invalidSymptoms.length > 0 ? (
              <>
                {selectedSymptoms.map((item) => (
                  <button
                    key={item}
                    type="button"
                    className="chip"
                    onClick={() => remove(item)}
                    aria-label={`Remove ${formatSymptom(item)}`}
                  >
                    <span>{formatSymptom(item)}</span>
                    <span className="chipRemove" aria-hidden="true">x</span>
                  </button>
                ))}
                {invalidSymptoms.map((item) => (
                  <button
                    key={item}
                    type="button"
                    className="chip invalidChip"
                    onClick={() => remove(item)}
                    aria-label={`Remove invalid symptom ${formatSymptom(item)}`}
                  >
                    <span>{formatSymptom(item)}</span>
                    <span className="chipRemove" aria-hidden="true">x</span>
                  </button>
                ))}
              </>
            ) : (
              <EmptyState
                icon="+"
                title="No symptoms added"
                message="Search, select, or use voice input to add symptoms."
              />
            )}
          </div>
          {invalidSymptoms.length > 0 && (
            <div className="invalidNotice">
              This symptom may not apply to the selected profile and will not be used for prediction.
            </div>
          )}

          <div className="tile profileTile">
            <div className="sectionHeading">
              <h3>Health Profile</h3>
              {profileApplied && <span className="savedBadge">Saved</span>}
            </div>
            <div className="grid2 profileGrid">
              {[
                ["name", "Name", "text", "Name"],
                ["age", "Age", "number", "Age"],
                ["gender", "Gender", "text", "Gender"],
                ["height", "Height (cm)", "number", "Height"],
                ["weight", "Weight (kg)", "number", "Weight"],
                ["conditions", "Pre-existing Conditions", "text", "e.g. diabetes, hypertension"],
                ["allergies", "Allergies", "text", "e.g. penicillin"],
              ].map(([field, label, type, placeholder]) => (
                <label key={field}>
                  {label}
                  <input
                    type={type}
                    value={profile[field]}
                    onChange={(e) => setProfile({ ...profile, [field]: e.target.value })}
                    placeholder={placeholder}
                  />
                </label>
              ))}
            </div>
            <button className="secondaryBtn" onClick={saveProfile}>
              Save Profile
            </button>
          </div>

          <button className="cta" onClick={predict} disabled={loading || selectedSymptoms.length === 0}>
            {loading ? "Analyzing..." : "Analyze Symptoms"}
          </button>

          {result && (
            <section className={`result${hasValidPrediction && topConfidence < 40 ? " resultSoft" : ""}`}>
              {!hasValidPrediction && (
                <div className="tile emptyPredictionState">
                  <div className="emptyIcon">!</div>
                  <h3>Insufficient Information</h3>
                  <p>Add more symptoms for a better prediction.</p>
                  {result.prediction_status === "Inconsistent symptoms" && (
                    <p style={{ color: "#ef4444", marginTop: "8px" }}>
                      Symptoms belong to too many unrelated body systems. Please review your selection.
                    </p>
                  )}
                </div>
              )}

              {hasValidPrediction && (
                <>
                  <div className="disease">
                    <div className="diseaseIcon">+</div>
                    <div>
                      <div className="diseaseHeader">
                        <h1>{topPrediction?.disease ?? "No strong prediction"}</h1>
                        {topConfidence >= 70 && (
                          <span className={`confidenceBadge high`}>
                            {confidenceLabel}
                          </span>
                        )}
                        {topConfidence >= 40 && topConfidence < 70 && (
                          <span className={`confidenceBadge medium`}>
                            {confidenceLabel}
                          </span>
                        )}
                        {topConfidence < 40 && (
                          <span className={`confidenceBadge low`}>
                            {confidenceLabel}
                          </span>
                        )}
                      </div>
                      <p className={topConfidence < 70 ? "confidenceSummary lowConfidenceText" : "confidenceSummary"}>
                        Confidence: {topPrediction?.confidence ?? "0.0%"}
                      </p>
                      {result.triage_level && (
                        <span className={`confidenceBadge ${result.triage_level === "Emergency" ? "high" : result.triage_level === "Urgent" ? "medium" : "low"}`}>
                          {result.triage_level}
                        </span>
                      )}
                    </div>
                  </div>

                  {result.red_flag_warning && (
                    <div className="warning-card">
                      <strong>{result.red_flag_warning}</strong>
                      <p>Red flag symptoms detected. Seek medical care promptly if symptoms are severe, worsening, or new.</p>
                    </div>
                  )}

                  {result.prediction_status === "Insufficient information" || (
                    result.prediction_status === "Prediction uncertain" && topConfidence < 50
                  ) && (
                    <div className="warning-card">
                      <strong>Review recommended</strong>
                      <p>Prediction confidence is limited. Add more symptoms or consult a clinician for guidance.</p>
                    </div>
                  )}

                  <div className="grid2">
                    <div className="tile metricTile">
                      <h3>Risk</h3>
                      <span className={`riskBadge ${riskClass(result.risk_level)}`}>
                        {result.risk_level}
                      </span>
                    </div>
                    <div className="tile metricTile">
                      <h3>Severity</h3>
                      <h2>{result.severity_score}</h2>
                    </div>
                    <div className="tile metricTile">
                      <h3>Triage</h3>
                      <span className={`confidenceBadge ${result.triage_level === "Emergency" ? "high" : result.triage_level === "Urgent" ? "medium" : "low"}`}>
                        {result.triage_level}
                      </span>
                    </div>
                  </div>

                  <div className="tile">
                    <div className="sectionHeading">
                      <h3>Recommended Doctor</h3>
                      <span className="specialtyBadge">{result.recommended_doctor}</span>
                    </div>
                    {result.health_profile_applied && (
                      <div className="profileSummary">
                        <p>Age: {result.health_profile.age || "Not provided"}</p>
                        <p>
                          Conditions:{" "}
                          {result.health_profile.conditions?.length > 0
                            ? result.health_profile.conditions.join(", ")
                            : "None"}
                        </p>
                      </div>
                    )}
                    <button
                      className="findNearbyBtn"
                      onClick={findNearbyDoctors}
                      disabled={nearbyLoading}
                    >
                      {nearbyLoading ? "Finding doctors..." : "Find Nearby Doctors"}
                    </button>
                    {locationError && <p className="locationError">{locationError}</p>}
                    {!nearbyLoading && !nearbySearched && (
                      <p className="subtleState smallNote">
                        Search nearby specialists for {result.recommended_doctor} after getting your diagnosis.
                      </p>
                    )}
                  </div>

                  {nearbyLoading && <div className="tile subtleState">Searching nearby providers...</div>}
                  {(nearbyDoctors.length > 0 || nearbySearched) && (
                    <div className="tile">
                      <h3>Nearby Doctors</h3>
                      {nearbyDoctors.length > 0 ? (
                        <div className="doctorGrid">
                          {nearbyDoctors.map((doc) => (
                            <div key={`${doc.name}-${doc.distance}`} className="nearbyDoctorItem">
                              <div className="doctorIcon" aria-hidden="true">+</div>
                              <div className="doctorDetails">
                                <h4>{doc.name}</h4>
                                <p>{doc.specialty}</p>
                              </div>
                              <span className="distanceBadge">{doc.distance}</span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <EmptyState
                          icon="!"
                          title="No nearby specialists available"
                          message="No nearby doctors matched this specialty. Try again or choose a general physician."
                        />
                      )}
                    </div>
                  )}

                  {result.description && (
                    <div className="tile readableBlock">
                      <h3>Description</h3>
                      <p>{result.description}</p>
                    </div>
                  )}

                  {result.disease_details && (
                    (result.disease_details.causes?.length > 0 ||
                      result.disease_details.symptoms?.length > 0 ||
                      result.disease_details.foods?.length > 0 ||
                      result.disease_details.exercise?.length > 0)
                  ) && (
                    <div className="tile infoGrid">
                      <h3>Disease Information</h3>
                      {result.disease_details.causes?.length > 0 && (
                        <p><b>Causes:</b> {result.disease_details.causes?.join(", ")}</p>
                      )}
                      {result.disease_details.symptoms?.length > 0 && (
                        <p><b>Symptoms:</b> {result.disease_details.symptoms?.join(", ")}</p>
                      )}
                      {result.disease_details.foods?.length > 0 && (
                        <p><b>Foods to Avoid:</b> {result.disease_details.foods?.join(", ")}</p>
                      )}
                      {result.disease_details.exercise?.length > 0 && (
                        <p><b>Exercise:</b> {result.disease_details.exercise?.join(", ")}</p>
                      )}
                    </div>
                  )}

                  <div className="tile">
                    <h3>Prediction Confidence</h3>
                    {hasPredictions ? (
                      result.predictions.map((item) => {
                        const percent = parseFloat(item.confidence)
                        const fillStyle = {
                          width: `${percent}%`,
                          background: confidenceColor(percent)
                        }

                        return (
                          <div key={item.disease} className="predictionBarContainer" title={`${item.disease}: ${percent}%`}>
                            <div className="predictionLabel">
                              <span>{item.disease}</span>
                              <span>{percent}%</span>
                            </div>
                            <div className="predictionBar">
                              <div className="predictionFill" style={fillStyle} />
                            </div>
                          </div>
                        )
                      })
                    ) : (
                      <p className="subtleState">
                        No high-confidence disease predictions were available. Add more symptoms or refine the details for a better result.
                      </p>
                    )}
                  </div>

                  {result.prediction_explanation && (
                    <div className="tile matchedSymptomsCard">
                      <div className="sectionHeading">
                        <h3>Matched Symptoms</h3>
                      </div>
                      {result.prediction_explanation.matched_symptoms?.length > 0 ? (
                        <div className="chips compactChips">
                          {result.prediction_explanation.matched_symptoms.map((symptom) => (
                            <span key={symptom} className="matchChip">
                              {formatSymptom(symptom)}
                            </span>
                          ))}
                        </div>
                      ) : (
                        <p>Limited symptom overlap detected. Consider adding more symptoms.</p>
                      )}
                      {result.prediction_explanation.symptom_utilization?.length > 0 && (
                        <div className="profileSummary">
                          {result.prediction_explanation.symptom_utilization.map((item) => (
                            <p key={item.symptom}>
                              {formatSymptom(item.symptom)}: {item.status}
                            </p>
                          ))}
                        </div>
                      )}
                      {result.prediction_explanation.suggested_symptoms?.length > 0 && (
                        <p className="reasonText">
                          Common missing symptoms: {result.prediction_explanation.suggested_symptoms.map((symptom) => formatSymptom(symptom)).join(", ")}
                        </p>
                      )}
                      {result.prediction_explanation.invalid_symptoms?.length > 0 && (
                        <p className="reasonText invalidNotice">
                          {`Excluded symptoms: ${result.prediction_explanation.invalid_symptoms
                            .map((symptom) => formatSymptom(symptom))
                            .join(", ")}`}
                        </p>
                      )}
                      {result.prediction_explanation.reason && (
                        <p className="reasonText">{result.prediction_explanation.reason}</p>
                      )}
                    </div>
                  )}

                  {suggestedSymptoms.length > 0 && (
                    <div className="tile">
                      <h3>Suggested Symptoms</h3>
                      <div className="chips">
                        {suggestedSymptoms.map((item) => (
                          <button key={item} type="button" className="chip" onClick={() => addSymptom(item)}>
                            + {formatSymptom(item)}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  <a
                    href={`${API}/download-report`}
                    target="_blank"
                    rel="noreferrer"
                    className="downloadBtn"
                  >
                    Download Report
                  </a>
                </>
              )}
            </section>
          )}

          <section className="result">
            <h2>Ask MedAssist</h2>
            <input
              className="search"
              placeholder="Ask a health question..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") askAI()
              }}
            />
            <button className="cta compactCta" onClick={askAI}>
              Ask
            </button>
            {chatReply && (
              <div className="tile">
                <h3>AI Response</h3>
                <p>{chatReply}</p>
              </div>
            )}
          </section>

          <section className="result">
            <div className="sectionHeading">
              <h2>Health Analytics</h2>
              {analyticsLoading && <span className="loadingText">Loading...</span>}
            </div>
            {!!analytics && analytics.total_predictions === 0 && (
              <EmptyState
                icon="i"
                title="No valid predictions yet"
                message="Run predictions with sufficient confidence to start building health insights."
              />
            )}
            {!!analytics && analytics.total_predictions > 0 && (
              <>
                <div className="analyticsCards">
                  <div className="tile analyticsCard">
                    <h3>Total Valid Predictions</h3>
                    <strong>{analytics.total_predictions}</strong>
                  </div>
                  <div className="tile analyticsCard">
                    <h3>Most Frequent Disease</h3>
                    <strong>{analytics.most_common_disease}</strong>
                  </div>
                  <div className="tile analyticsCard">
                    <h3>Risk Distribution</h3>
                    <div className="riskRows">
                      <span><i className="dot riskLowDot" /> Low: {analytics.risk_distribution.Low}</span>
                      <span><i className="dot riskMediumDot" /> Medium: {analytics.risk_distribution.Medium}</span>
                      <span><i className="dot riskHighDot" /> High: {analytics.risk_distribution.High}</span>
                    </div>
                  </div>
                </div>

                {trendData.length === 1 && (
                  <div className="tile trendSummary">
                    <h3>Recent Severity Trend</h3>
                    <strong>{trendData[0].severity}</strong>
                    <p>{trendData[0].fullLabel}</p>
                    <span>More predictions are needed to draw a trend.</span>
                  </div>
                )}

                {trendData.length >= 2 && (
                  <div className="analyticsChart">
                    <h3>Recent Severity Trend</h3>
                    <div className="chartFrame">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart
                          data={trendData}
                          margin={{ top: 16, right: 22, left: 4, bottom: 42 }}
                        >
                          <CartesianGrid strokeDasharray="3 3" stroke="#e7ecef" />
                          <XAxis
                            dataKey="label"
                            interval={0}
                            angle={-18}
                            textAnchor="end"
                            height={54}
                            tick={{ fontSize: 12, fill: "#5f6870" }}
                            tickMargin={14}
                          />
                          <YAxis tick={{ fontSize: 12, fill: "#5f6870" }} width={38} />
                          <Tooltip content={<SeverityTooltip />} />
                          <Line
                            type="natural"
                            dataKey="severity"
                            stroke="#3b82a0"
                            strokeWidth={3}
                            dot={{ r: 4, fill: "#ffffff", strokeWidth: 2 }}
                            activeDot={{ r: 6, fill: "#3b82a0" }}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                )}
              </>
            )}
          </section>

          <section className="result recentPredictions">
            <h2>Recent Predictions</h2>
            {history.length > 0 ? (
              <div className="recentGrid">
                {history.map((item) => {
                  const symptomPreview = formatSymptomList(item.symptoms)
                  return (
                    <div key={item.id} className="predictionCard">
                      <div className="predictionCardTop">
                        <strong>{item.disease}</strong>
                        <span className={`riskBadge ${riskClass(item.risk)}`}>{item.risk}</span>
                      </div>
                      <p title={symptomPreview}>{truncateLabel(symptomPreview, 48)}</p>
                      <div className="predictionMeta">
                        <span>Severity {item.severity}</span>
                        <span>{item.time}</span>
                      </div>
                    </div>
                  )
                })}
              </div>
            ) : (
              <EmptyState
                icon="i"
                title="No predictions yet"
                message="Your recent analyses will appear here after you run a prediction."
              />
            )}
          </section>
        </section>
      </main>

      <footer className="footer">
        <strong>MedAssist AI</strong>
        <p>AI-powered symptom analysis and health insights.</p>
        <p>{MEDICAL_DISCLAIMER}</p>
      </footer>
    </div>
  )
}

export default App
