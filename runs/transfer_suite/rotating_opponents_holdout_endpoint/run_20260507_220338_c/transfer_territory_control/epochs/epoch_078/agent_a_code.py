def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocks = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocks.add((x, y))

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_terr.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.add((x, y))

    cx, cy = (w // 2, h // 2)
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_dx, best_dy = 0, 0
    best = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocks:
            continue

        distc = abs(nx - cx) + abs(ny - cy)
        score = -distc

        if (nx, ny) in opp_terr:
            score += 1.2  # likely flip/capture value
            score += 0.1 * (abs(ox - ny) + abs(oy - nx) == 0)
        if (nx, ny) in unclaimed:
            score += 0.35

        # Prefer moves that reduce distance to the opponent to contest center-ish
        score += 0.08 * (-(abs(nx - ox) + abs(ny - oy)) + (abs(sx - ox) + abs(sy - oy)))

        # Small deterministic tie-breaker
        score += 0.00001 * (nx * 31 + ny * 17)

        if score > best:
            best = score
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]