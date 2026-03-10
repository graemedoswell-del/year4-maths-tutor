
import random

TOPICS = ["place_value", "addition", "subtraction", "multiplication", "division", "fractions", "measurement", "geometry", "statistics"]

def accuracy(data, topic):
    t = data["topics"][topic]
    if t["total"] == 0:
        return None
    return t["correct"] / t["total"]

def choose_topic(data, current_world):
    if current_world == 10:
        weak = []
        for t in TOPICS:
            a = accuracy(data, t)
            if a is not None and a < 0.7:
                weak.append(t)
        if weak and random.random() < 0.7:
            return random.choice(weak)
        return random.choice(TOPICS)

    world_map = {
        1: "place_value",
        2: "addition",
        3: "subtraction",
        4: "multiplication",
        5: "division",
        6: "fractions",
        7: "measurement",
        8: "geometry",
        9: "statistics"
    }
    topic = world_map.get(current_world, "addition")

    weak = []
    for t in TOPICS:
        a = accuracy(data, t)
        if a is not None and a < 0.6:
            weak.append(t)
    if weak and random.random() < 0.35:
        return random.choice(weak)
    return topic

def generate_question(topic, level=1):
    if topic == "place_value":
        kind = random.choice(["value", "compare", "round", "order"])
        if kind == "value":
            n = random.randint(1000, 9999)
            idx = random.randint(0, 3)
            digit = str(n)[idx]
            place_values = [1000, 100, 10, 1]
            answer = int(digit) * place_values[idx]
            question = f"What is the value of the digit {digit} in {n}?"
            explanation = f"The digit {digit} is in the {['thousands','hundreds','tens','ones'][idx]} place, so its value is {answer}."
            return question, str(answer), explanation
        if kind == "compare":
            a = random.randint(1000, 9999)
            b = random.randint(1000, 9999)
            answer = ">" if a > b else "<" if a < b else "="
            question = f"Fill in the sign: {a} __ {b}"
            explanation = f"Compare from left to right. The correct sign is {answer}."
            return question, answer, explanation
        if kind == "round":
            n = random.randint(100, 9999)
            place = random.choice([10, 100, 1000])
            answer = str(round(n / place) * place)
            question = f"Round {n} to the nearest {place}."
            explanation = f"Look at the digit to the right of the {place} place. The rounded answer is {answer}."
            return question, answer, explanation
        nums = [random.randint(1000, 9999) for _ in range(3)]
        answer = ", ".join(str(x) for x in sorted(nums))
        question = f"Put these in order from smallest to largest: {nums[0]}, {nums[1]}, {nums[2]}"
        explanation = f"The numbers in order are {answer}."
        return question, answer, explanation

    if topic == "addition":
        a = random.randint(100 + level*5, 4999)
        b = random.randint(100, 4999)
        answer = str(a + b)
        question = f"{a} + {b} = ?"
        explanation = "Line up the place values and add ones, then tens, then hundreds and thousands."
        return question, answer, explanation

    if topic == "subtraction":
        a = random.randint(500 + level*5, 4999)
        b = random.randint(100, min(2500, a-1))
        answer = str(a - b)
        question = f"{a} - {b} = ?"
        explanation = "Subtract each column carefully. If needed, regroup from the next column."
        return question, answer, explanation

    if topic == "multiplication":
        if random.random() < 0.6:
            a = random.randint(2, 12)
            b = random.randint(2, 12)
        else:
            a = random.randint(10, 40)
            b = random.randint(2, 9)
        answer = str(a * b)
        question = f"{a} × {b} = ?"
        explanation = "Use times tables or split the number into easier parts."
        return question, answer, explanation

    if topic == "division":
        b = random.randint(2, 12)
        ans = random.randint(2, 12)
        a = b * ans
        answer = str(ans)
        question = f"{a} ÷ {b} = ?"
        explanation = "Think of the multiplication fact that matches this division."
        return question, answer, explanation

    if topic == "fractions":
        mode = random.choice(["of_amount", "add_same_den", "equiv"])
        if mode == "of_amount":
            d = random.choice([2, 3, 4, 5, 6, 8, 10])
            n = random.randint(1, d-1)
            base = d * random.randint(2, 12)
            answer = str(int((n / d) * base))
            question = f"What is {n}/{d} of {base}?"
            explanation = f"First divide {base} by {d}, then multiply by {n}."
            return question, answer, explanation
        if mode == "add_same_den":
            d = random.choice([4, 5, 6, 8, 10])
            a = random.randint(1, d-1)
            b = random.randint(1, d-a)
            answer = f"{a+b}/{d}"
            question = f"{a}/{d} + {b}/{d} = ?"
            explanation = "Add the numerators and keep the denominator the same."
            return question, answer, explanation
        a, b = random.choice([(1,2),(1,3),(2,3),(1,4),(3,4)])
        mul = random.choice([2,3,4])
        answer = f"{a*mul}/{b*mul}"
        question = f"Write an equivalent fraction to {a}/{b}."
        explanation = "Multiply the top and bottom by the same number."
        return question, answer, explanation

    if topic == "measurement":
        mode = random.choice(["perimeter","time","money","convert"])
        if mode == "perimeter":
            l = random.randint(2, 12)
            w = random.randint(2, 12)
            answer = str(2*l + 2*w)
            question = f"What is the perimeter of a rectangle with length {l} cm and width {w} cm?"
            explanation = "Perimeter means the distance around the edge, so add all the sides."
            return question, answer, explanation
        if mode == "time":
            hours = random.randint(1, 11)
            mins = random.choice([0, 15, 30, 45])
            suffix = random.choice(["am", "pm"])
            h24 = hours if suffix == "am" and hours != 12 else 0 if suffix == "am" else hours + 12 if hours != 12 else 12
            answer = f"{h24:02d}:{mins:02d}"
            question = f"Write {hours}:{mins:02d} {suffix} in 24-hour time."
            explanation = "For pm times, add 12 to the hour unless it is 12 pm."
            return question, answer, explanation
        if mode == "money":
            pounds = random.randint(2, 20)
            pence = random.choice([0, 25, 50, 75])
            cost_pounds = random.randint(1, pounds-1)
            cost_pence = random.choice([0, 25, 50, 75])
            total = pounds*100 + pence
            cost = cost_pounds*100 + cost_pence
            answer_pence = total - cost
            answer = f"£{answer_pence//100}.{answer_pence%100:02d}"
            question = f"You have £{pounds}.{pence:02d}. You spend £{cost_pounds}.{cost_pence:02d}. How much is left?"
            explanation = "Convert to pence, subtract, then convert back to pounds and pence."
            return question, answer, explanation
        cm = random.choice([100, 200, 300, 400, 500, 1000])
        answer = str(cm // 100)
        question = f"Convert {cm} cm into metres."
        explanation = "100 cm = 1 metre, so divide by 100."
        return question, answer, explanation

    if topic == "geometry":
        mode = random.choice(["shape","symmetry","angle","coordinates"])
        if mode == "shape":
            answer = "square"
            question = "Which shape has 4 equal sides and 4 right angles?"
            explanation = "A square has 4 equal sides and 4 right angles."
            return question, answer, explanation
        if mode == "symmetry":
            answer = "2"
            question = "How many lines of symmetry does a rectangle have?"
            explanation = "A rectangle has 2 lines of symmetry."
            return question, answer, explanation
        if mode == "angle":
            answer = "right angle"
            question = "What do we call an angle of 90°?"
            explanation = "An angle of 90° is a right angle."
            return question, answer, explanation
        x = random.randint(1, 5)
        y = random.randint(1, 5)
        answer = f"({x},{y})"
        question = f"Write the coordinate that is {x} across and {y} up."
        explanation = "Coordinates are written as (across, up)."
        return question, answer, explanation

    if topic == "statistics":
        apples = random.randint(2, 12)
        pears = random.randint(2, 12)
        answer = str(abs(apples - pears))
        question = f"A chart shows {apples} apples and {pears} pears. How many more of the larger fruit were there?"
        explanation = "Find the difference between the two amounts."
        return question, answer, explanation

    return "2 + 2 = ?", "4", "2 and 2 make 4."

def generate_sats_paper():
    arithmetic = []
    reasoning = []
    problem = []

    topics = ["addition","subtraction","multiplication","division","fractions","measurement","geometry","place_value"]
    for _ in range(10):
        t = random.choice(topics[:6])
        arithmetic.append(generate_question(t, 1)[0])

    for _ in range(5):
        t = random.choice(topics)
        reasoning.append(generate_question(t, 1)[0])

    for _ in range(5):
        t = random.choice(["measurement","fractions","statistics","place_value","multiplication"])
        problem.append(generate_question(t, 1)[0])

    return {
        "arithmetic": arithmetic,
        "reasoning": reasoning,
        "problem": problem
    }
