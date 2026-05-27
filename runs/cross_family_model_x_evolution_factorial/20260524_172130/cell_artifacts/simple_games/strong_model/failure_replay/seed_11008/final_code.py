def choose_move(observation):
    def clamp_step(v):
        return -1 if v < 0 else (1 if v > 0 else 0)

    def pos(v, default=(0, 0)):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return v[0], v[1]
        return default

    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def sign_toward(a, b):
        return [clamp_step(b[0] - a[0]), clamp_step(b[1] - a[1])]

    def safe_list(v):
        return v if isinstance(v, list) else []

    env = observation.get("environment_name", "") or ""
    sx, sy = pos(observation.get("self_position"))
    ox, oy = pos(observation.get("opponent_position"), (sx, sy))
    me = (sx, sy)
    opp = (ox, oy)
    w = observation.get("grid_width", 0) or 0
    h = observation.get("grid_height", 0) or 0

    resources = []
    for item in safe_list(observation.get("resources")):
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            resources.append((item[0], item[1]))

    unclaimed = []
    for item in safe_list(observation.get("unclaimed_cells")):
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            unclaimed.append((item[0], item[1]))

    opp_terr = []
    for item in safe_list(observation.get("opponent_territory")):
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            opp_terr.append((item[0], item[1]))

    role = observation.get("self_role", "")
    if env == "pursuit_evasion":
        if role == "pursuer":
            return sign_toward(me, opp)
        corners = []
        if w and h:
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        else:
            corners = [(-10, -10), (-10, 10), (10, -10), (10, 10)]
        target = max(corners, key=lambda c: manhattan(c, opp))
        return sign_toward(me, target)

    if env == "territory_control":
        targets = unclaimed or opp_terr
        if targets:
            target = min(targets, key=lambda c: manhattan(c, me) * 2 - manhattan(c, opp))
            return sign_toward(me, target)
        if w and h:
            center = ((w - 1) // 2, (h - 1) // 2)
            return sign_toward(me, center)
        return [0, 0]

    if resources:
        target = min(resources, key=lambda c: manhattan(c, me) + max(0, 3 - manhattan(c, opp)))
        return sign_toward(me, target)

    if opp != me:
        return sign_toward(me, opp)

    if w and h:
        return sign_toward(me, ((w - 1) // 2, (h - 1) // 2))

    return [0, 0]
