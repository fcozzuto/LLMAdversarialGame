def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def clamp01(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    # If no visible resources, move toward the safest corner away from opponent.
    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        for cx, cy in corners:
            if (cx, cy) in obstacles:
                continue
            d = abs(cx - sx) + abs(cy - sy)
            od = abs(cx - ox) + abs(cy - oy)
            score = (od - d)  # prefer far from opponent and not too far from us
            if best is None or score > best[0]:
                best = (score, cx, cy)
        if best is None:
            return [0, 0]
        cx, cy = best[1], best[2]
        dx = clamp01(cx - sx)
        dy = clamp01(cy - sy)
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles:
            return [0, 0]
        return [dx, dy]

    # Choose target resource where we can arrive earlier (with margin), else deny high-value proximity.
    bestT = None
    for x, y in resources:
        if (x, y) in obstacles:
            continue
        myd = max(abs(x - sx), abs(y - sy))  # Chebyshev matches diagonal moves
        opd = max(abs(x - ox), abs(y - oy))
        margin = myd - opd  # negative is good
        # Secondary tie-break: prefer closer to reduce time-to-collection
        score = (-1000 * margin) - (0.01 * (myd + opd))
        if bestT is None or score > bestT[0]:
            bestT = (score, x, y)
    tx, ty = bestT[1], bestT[2]

    # Move one step toward target with diagonal preference; avoid stepping into obstacles.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                dist = max(abs(tx - nx), abs(ty - ny))
                opd_after = max(abs(tx - ox), abs(ty - oy))  # keep opponent term mild/deterministic
                # Prefer decreasing dist; also prefer diagonals to close faster.
                candidates.append((dist + 0.2 * (0 if dx != 0 and dy != 0 else 1), -abs(dx) - abs(dy), dx, dy))
    # If target is adjacent but blocked, fall back to any move that increases our lead locally.
    if not candidates:
        return [0, 0]

    candidates.sort()
    return [int(candidates[0][2]), int(candidates[0][3])]