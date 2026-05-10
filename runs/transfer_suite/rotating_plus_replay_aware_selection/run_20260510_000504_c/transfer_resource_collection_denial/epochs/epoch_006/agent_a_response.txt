def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, dict):
            if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                res.append((int(r["position"][0]), int(r["position"][1])))
            elif "x" in r and "y" in r:
                res.append((int(r["x"]), int(r["y"])))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))
    if not res:
        return [0, 0]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy, nx, ny))

    # Choose target: prefer resources we can reach no slower than opponent, then closer, then deterministic by coords.
    best_t = None
    best_key = None
    for tx, ty in sorted(res):
        if (tx, ty) in obstacles:
            continue
        d1 = man((sx, sy), (tx, ty))
        d2 = man((ox, oy), (tx, ty))
        # Encourage breaking ties in our favor; penalize if opponent is significantly closer.
        key = (
            (d1 - d2),          # smaller better
            d1,                 # closer for us
            -((tx + 1) * 101 + (ty + 1)),  # deterministic bias toward "larger" coords when equal
            tx, ty
        )
        if best_key is None or key < best_key:
            best_key = key
            best_t = (tx, ty)
    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    # Evaluate next moves using a local greedy score with obstacle penalty and opponent pressure.
    best_move = (0, 0, sx, sy)
    best_score = None
    for dx, dy, nx, ny in moves:
        if (nx, ny) in obstacles:
            continue
        our_d = man((nx, ny), (tx, ty))
        opp_d = man((ox, oy), (tx, ty))
        # If we are behind opponent, push harder by prioritizing smaller our_d relative to opp_d.
        score = (our_d - opp_d, our_d, abs(nx - tx) + abs(ny - ty), tx, ty)
        # Add obstacle avoidance: discourage moving into cells adjacent to obstacles (local clutter).
        adj = 0
        for axd in (-1, 0, 1):
            for ayd in (-1, 0, 1):
                if axd == 0 and ayd == 0:
                    continue
                px, py = nx + axd, ny + ayd
                if (px, py) in obstacles:
                    adj += 1
        score = (score[0], score[1] + 0.1 * adj, score[2] + 0.01 * adj, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy, nx, ny)

    return [int(best_move[0]), int(best_move[1])]