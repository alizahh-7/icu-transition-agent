async function startDischarge() {

    const patientId =
        document.getElementById('patientId').value;

    const icuDays =
        parseInt(document.getElementById('icuDays').value);

    const startBtn =
        document.getElementById('startBtn');

    const resultsCard =
        document.getElementById('resultsCard');

    resultsCard.classList.remove('show');

    startBtn.disabled = true;

    startBtn.textContent =
        '⏳ Coordinating Agents...';

    for (let i = 1; i <= 4; i++) {

        const agent =
            document.getElementById(`agent${i}`);

        agent.className = 'agent-card';

        agent.querySelector('.status-icon').className =
            'status-icon status-pending';
    }

    try {

        const agents =
            ['agent1', 'agent2', 'agent3', 'agent4'];

        let current = 0;

        const interval = setInterval(() => {

            if (current < agents.length) {

                const agent =
                    document.getElementById(agents[current]);

                agent.className =
                    'agent-card active';

                agent.querySelector('.status-icon').className =
                    'status-icon status-active';

                current++;

            }

        }, 1000);

        const response = await fetch(
            'http://127.0.0.1:8010/icu-discharge-fhir',
            {
                method:'POST',

                headers:{
                    'Content-Type':'application/json'
                },

                body:JSON.stringify({
                    fhir_patient_id:patientId,
                    icu_days:icuDays
                })
            }
        );

        clearInterval(interval);

        const data = await response.json();

        for (let i = 1; i <= 4; i++) {

            const agent =
                document.getElementById(`agent${i}`);

            agent.className =
                'agent-card complete';

            agent.querySelector('.status-icon').className =
                'status-icon status-complete';
        }

        document.getElementById('patientInfo').innerHTML = `
            <h3>Patient Overview</h3>

            <p><strong>Name:</strong> ${data.patient_name}</p>

            <p><strong>Age:</strong> ${data.patient_age}</p>

            <p><strong>Diagnosis:</strong> ${data.diagnosis}</p>
        `;

        document.getElementById('summary').innerText =
            data.discharge_packet.clinical_summary;

        document.getElementById('risks').innerText =
            data.discharge_packet.readmission_risks;

        document.getElementById('carePlan').innerText =
            data.discharge_packet.care_coordination_plan;

        document.getElementById('priorAuth').innerText =
            data.discharge_packet.prior_auth_justification;

        resultsCard.classList.add('show');

    } catch(error) {

        alert(error);

        console.error(error);

    } finally {

        startBtn.disabled = false;

        startBtn.textContent =
            '🚀 Start Discharge Coordination';
    }
}
.robot-label {
    position: absolute;
    bottom: 10px;
    left: 0;
    right: 0;

    text-align: center;

    color: white;

    font-size: 12px;

    font-weight: 600;

    letter-spacing: 1px;

    text-shadow: 0 0 10px rgba(0,255,255,0.8);
}