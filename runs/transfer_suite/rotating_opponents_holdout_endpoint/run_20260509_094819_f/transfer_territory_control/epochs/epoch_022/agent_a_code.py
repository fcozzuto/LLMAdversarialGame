def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    unclaimed = observation.get("unclaimed_cells") or []
    if isinstance(unclaimed, dict):
        unclaimed = list(unclaimed.keys())
    unclaimed_set = set(tuple(p) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2)
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def manh(x, y, a, b): return abs(x - a) + abs(y - b)

    # Nearest objective distance among unclaimed (prefer closing distance deterministically)
    objs = list(unclaimed_set)
    if not objs:
        objs = [p for p in opp_terr] + [p for p in self_terr]
    def nearest_dist(x, y):
        best = 10**9
        for ox, oy in objs[:32]:
            d = manh(x, y, ox, oy)
            if d < best: best = d
        return best

    # One-step greedy with deterministic tie-break
    best = None
    best_h = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in self_terr: base = 1
        elif (nx, ny) in unclaimed_set: base = 8
        elif (nx, ny) in opp_terr: base = 5
        else: base = 0
        # Territory leaders bonus not modeled; we focus on immediate gain and distance closure.
        d = nearest_dist(nx, ny)
        # Lower d is better; prefer unclaimed over opponent territory; small bias for stable movement
        h = base * 1000 - d * 10 - (dx * dx + dy * dy)
        key = (h, -base, d, dx, dy)
        if best is None or key > best:
            best = key
            best_move = [dx, dy]
    if best is None:
        return [0, 0]
    return best_move