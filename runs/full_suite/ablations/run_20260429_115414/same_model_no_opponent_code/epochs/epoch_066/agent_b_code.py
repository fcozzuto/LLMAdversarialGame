def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    best_moves = []
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    # Find nearest resource if possible
    target = None
    bestd = 10**9
    for r in resources:
        if r and len(r) >= 2:
            tx, ty = int(r[0]), int(r[1])
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obs:
                d = abs(tx - sx) + abs(ty - sy)
                if d < bestd:
                    bestd = d
                    target = (tx, ty)

    scored = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Prefer moving closer to target; otherwise move away from opponent.
        if target is not None:
            tx, ty = target
            score = -(abs(tx - nx) + abs(ty - ny))
        else:
            score = abs(ox - nx) + abs(oy - ny)
        # Small deterministic tie-breaker: prefer not staying still unless forced
        score -= 0.001 if (dx == 0 and dy == 0) else 0.0
        scored.append((score, dx, dy))

    if not scored:
        # All neighbors blocked: deterministic fallback
        return [0, 0]

    scored.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(scored[0][1]), int(scored[0][2])]