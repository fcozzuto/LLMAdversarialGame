def choose_move(observation):
    def to_xy(v):
        if isinstance(v, (list, tuple)) and len(v) == 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict):
            p = v.get("position", v.get("pos", None))
            if isinstance(p, (list, tuple)) and len(p) == 2:
                return int(p[0]), int(p[1])
        return None

    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = to_xy(observation.get("self_position", [0, 0])) or (0, 0)
    ox, oy = to_xy(observation.get("opponent_position", [0, 0])) or (0, 0)

    obs_set = set()
    for o in (observation.get("obstacles", []) or []):
        t = to_xy(o)
        if t:
            x, y = t
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        t = to_xy(r)
        if t:
            x, y = t
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs_set:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Targeting change vs nearest_resource: prioritize resources we can reach first
    best = None
    for rx, ry in resources:
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        # Prefer winning races; if losing, pick least-distant.
        if sd <= od:
            # Extra preference for larger lead and for being in opponent's "shadow" (harder for opponent to retarget).
            lead = (od - sd)
            score = (1, lead, -sd, rx + ry)
        else:
            # Losing race: minimize our time; also slightly discourage letting opponent be much closer.
            score = (0, -sd, (sd - od), rx + ry)
        if best is None or score > best[0]:
            best = (score, (rx, ry))

    tx, ty = best[1]

    def step_score(nx, ny):
        if (nx, ny) in obs_set:
            return (-10**9, 0)
        # Greedy toward target with tie-break by denying opponent proximity
        d_self = dist((nx, ny), (tx, ty))
        d_opp = dist((nx, ny), (ox, oy))
        # Also consider staying within bounds only via validity check
        return (-d_self, -d_opp)

    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
            cand.append((step_score(nx, ny), [dx, dy]))

    if cand:
        cand.sort(key=lambda x: (x[0][0], x[0][1]), reverse=True)
        return cand[0][1]

    return [0, 0]