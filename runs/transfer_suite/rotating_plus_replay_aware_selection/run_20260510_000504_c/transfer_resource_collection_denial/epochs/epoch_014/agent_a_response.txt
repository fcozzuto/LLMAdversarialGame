def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    res = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                res.append((int(r["position"][0]), int(r["position"][1])))
            elif "x" in r and "y" in r:
                res.append((int(r["x"]), int(r["y"])))
    res = [p for p in res if p not in obstacles]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(a, b, c, d): return abs(a - c) + abs(b - d)

    if not res:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
        return [0, 0]

    # Target resource: prioritize ones we can reach sooner than opponent.
    best = None
    for tx, ty in res:
        ds = md(sx, sy, tx, ty)
        do = md(ox, oy, tx, ty)
        # Larger advantage better; secondary prefer closer overall.
        key = (-(do - ds), ds, tx, ty)
        if best is None or key < best[0]:
            best = (key, (tx, ty))
    tx, ty = best[1]

    # Choose move among 9 deltas with deterministic tie-breaking.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            # Soft "blocking": if opponent is closer to this cell than we are, penalize.
            d_to_target = md(nx, ny, tx, ty)
            d_opp_cell = md(ox, oy, nx, ny)
            d_our_cell = md(sx, sy, nx, ny)
            opp_pressure = 0 if d_opp_cell >= d_our_cell else (d_our_cell - d_opp_cell)
            # Prefer decreasing target distance; keep determinism by fixed ordering.
            val = (d_to_target, opp_pressure, abs(dx) + abs(dy), dx, dy)
            candidates.append((val, [dx, dy]))
    candidates.sort(key=lambda t: t[0])
    return candidates[0][1] if candidates else [0, 0]