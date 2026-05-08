def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles", []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            legal.append((nx, ny, dx, dy))
    if not legal:
        return [0, 0]

    sr = str(observation.get("self_role", "")).lower()
    pursuer = ("purs" in sr) or ("hunter" in sr) or ("tagger" in sr) or ("pursuer" in sr)

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    resources = []
    for r in observation.get("resources", []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((r[0], r[1]))
        elif isinstance(r, dict) and "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
            resources.append((r["position"][0], r["position"][1]))

    rem = observation.get("remaining_resource_count", None)
    use_resource = bool(resources) and (rem is None or int(rem) > 0)
    if use_resource:
        target = min(resources, key=lambda p: md((sx, sy), p))
        better = lambda d: d  # minimize
    else:
        target = (ox, oy)
        if pursuer:
            better = lambda d: d  # minimize distance to opponent
        else:
            better = lambda d: -d  # maximize distance from opponent

    best = None
    bestv = None
    for nx, ny, dx, dy in legal:
        d = md((nx, ny), target)
        v = better(d)
        if best is None or v < bestv if bestv is not None else True:
            best = (dx, dy)
            bestv = v
        elif v == bestv:
            # deterministic tie-break: prefer closer to opponent (or farther if evasion), then stay
            oppd = md((nx, ny), (ox, oy))
            curr_oppd = md((sx + best[0], sy + best[1]), (ox, oy))
            if (pursuer and oppd < curr_oppd) or ((not pursuer) and oppd > curr_oppd) or (dx == 0 and dy == 0 and not (best[0] == 0 and best[1] == 0)):
                best = (dx, dy)
                bestv = v

    return [int(best[0]), int(best[1])]