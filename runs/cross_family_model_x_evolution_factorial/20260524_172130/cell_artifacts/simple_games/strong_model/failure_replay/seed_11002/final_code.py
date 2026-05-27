def choose_move(observation):
    def clamp_step(v):
        return -1 if v < 0 else (1 if v > 0 else 0)

    def pos(item):
        if item is None:
            return None
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            return item[0], item[1]
        if isinstance(item, dict):
            if "position" in item:
                p = item.get("position")
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    return p[0], p[1]
            x = item.get("x")
            y = item.get("y")
            if x is not None and y is not None:
                return x, y
        return None

    def first_pos(seq):
        if not seq:
            return None
        for it in seq:
            p = pos(it)
            if p is not None:
                return p
        return None

    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def step_toward(a, b):
        return [clamp_step(b[0] - a[0]), clamp_step(b[1] - a[1])]

    def step_away(a, b):
        return [clamp_step(a[0] - b[0]), clamp_step(a[1] - b[1])]

    def bounds():
        w = observation.get("grid_width", observation.get("width", 0)) or 0
        h = observation.get("grid_height", observation.get("height", 0)) or 0
        return w, h

    env = observation.get("environment_name", "resource_collection")
    self_p = pos(observation.get("self_position")) or (0, 0)
    opp_p = pos(observation.get("opponent_position")) or self_p
    w, h = bounds()

    if env == "pursuit_evasion":
        role = observation.get("self_role", observation.get("role", "pursuer"))
        if role == "pursuer":
            return step_toward(self_p, opp_p)

        corners = []
        if w > 0 and h > 0:
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        if not corners:
            return step_away(self_p, opp_p)

        target = corners[0]
        best = -1
        for c in corners:
            d = manhattan(c, opp_p)
            if d > best:
                best = d
                target = c
        return step_toward(self_p, target)

    if env == "territory_control":
        targets = observation.get("unclaimed_cells") or observation.get("opponent_territory") or observation.get("targets") or []
        t = first_pos(targets)
        if t is not None:
            return step_toward(self_p, t)

        home = pos(observation.get("home_base")) or pos(observation.get("base")) or None
        if home is not None:
            return step_toward(self_p, home)

        return step_away(self_p, opp_p)

    resources = observation.get("resources") or observation.get("resource_positions") or observation.get("food") or []
    r = first_pos(resources)
    if r is not None:
        return step_toward(self_p, r)

    danger = observation.get("danger_zones") or observation.get("walls") or []
    d = first_pos(danger)
    if d is not None:
        return step_away(self_p, d)

    if opp_p != self_p:
        return step_away(self_p, opp_p)
    return [0, 0]
