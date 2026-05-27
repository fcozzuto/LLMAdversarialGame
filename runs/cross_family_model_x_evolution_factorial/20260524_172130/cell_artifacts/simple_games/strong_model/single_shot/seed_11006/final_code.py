def choose_move(observation):
    def get(keys, default=None):
        if isinstance(observation, dict):
            for k in keys:
                v = observation.get(k, None)
                if v is not None:
                    return v
        return default

    def pair(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return v[0], v[1]
        return None

    p = pair(get(("self_position", "position", "self_pos", "pos", "location")))
    if p is None and isinstance(observation, dict):
        p = pair(get(("self",), None))
        if p is None and isinstance(observation.get("self"), dict):
            p = pair(observation["self"].get("position", observation["self"].get("pos")))
    if p is None:
        return [0, 0]

    ox = pair(get(("opponent_position", "opponent_pos")))
    resources = get(("resources",), []) or []
    obstacles = set()
    for v in get(("obstacles",), []) or []:
        t = pair(v)
        if t is not None:
            obstacles.add(t)
    if ox is not None:
        obstacles.add(ox)

    w = int(get(("grid_width",), 0) or 0)
    h = int(get(("grid_height",), 0) or 0)
    best = None
    bd = 10**9
    for r in resources:
        t = pair(r)
        if t is None or t == p:
            continue
        d = abs(t[0] - p[0]) + abs(t[1] - p[1])
        if d < bd or (d == bd and (t[0], t[1]) < best):
            bd, best = d, t

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    scored = []
    for dx, dy in moves:
        x, y = p[0] + dx, p[1] + dy
        if (w and (x < 0 or x >= w)) or (h and (y < 0 or y >= h)) or (x, y) in obstacles:
            continue
        s = 0
        if best is not None:
            s -= abs(best[0] - x) + abs(best[1] - y)
        if ox is not None:
            s += abs(ox[0] - x) + abs(ox[1] - y)
        scored.append((s, -abs(dx) - abs(dy), -dy, -dx, dx, dy))
    if scored:
        scored.sort(reverse=True)
        return [scored[0][4], scored[0][5]]
    return [0, 0]
