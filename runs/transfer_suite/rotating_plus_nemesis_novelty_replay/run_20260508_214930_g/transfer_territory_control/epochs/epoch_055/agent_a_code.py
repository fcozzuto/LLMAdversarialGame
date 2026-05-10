def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not dirs:
        return [0, 0]

    targets = list(unclaimed) if unclaimed else list(opp_t) if opp_t else []
    base_dist = abs(sx - ox) + abs(sy - oy)

    def nearest_score(px, py):
        if not targets:
            return 0
        dmin = 10**9
        best = None
        for tx, ty in targets[:24]:
            d = abs(tx - px) + abs(ty - py)
            if d < dmin or (d == dmin and (ty, tx) < best):
                dmin = d
                best = (ty, tx)
        if dmin == 10**9:
            return 0
        return -dmin

    best = [0, 0]
    best_score = -10**18
    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not ok(nx, ny):
            continue

        score = 0

        if (nx, ny) in opp_t:
            score += 2200
        if (nx, ny) in unclaimed:
            score += 90
        if (nx, ny) in self_t:
            score += 8

        # Push toward opponent to deny/flip more quickly (deterministic pressure).
        score += (base_dist - (abs(nx - ox) + abs(ny - oy))) * 6

        # Prefer moving toward nearby expansion targets.
        score += nearest_score(nx, ny) * 3

        # Mild bias: keep progressing along an "escape-free" direction
        # by discouraging steps that move away from both opponent and nearest target.
        away = (abs(nx - ox) + abs(ny - oy)) - base_dist
        score -= max(0, away) * 8

        # Discourage repeated stagnation: staying still is only OK if it's on frontier.
        if ddx == 0 and ddy == 0:
            if (sx, sy) in unclaimed or (sx, sy) in opp_t:
                score += 5
            else:
                score -= 25

        if score > best_score:
            best_score = score
            best = [ddx, ddy]

    return [int(best[0]), int(best[1])]