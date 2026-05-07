def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def mhd(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # Pick target to maximize our capture advantage; if we are already ahead, still prefer closeness.
    best_t = resources[0]
    best_v = -10**18
    for rx, ry in resources:
        sd = mhd(sx, sy, rx, ry)
        od = mhd(ox, oy, rx, ry)
        ahead = od - sd  # positive means we are closer
        # Bias slightly toward resources on/near opponent's current row to disrupt nearest-resource runs.
        disrupt = 3 if ry == oy else (1 if abs(ry - oy) == 1 else 0)
        v = 1000 * ahead - 2 * sd + disrupt
        if v > best_v:
            best_v = v
            best_t = (rx, ry)
    tx, ty = best_t

    # Choose among 8 directions + stay: greedily minimize distance while not moving into obstacles.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        dist = mhd(nx, ny, tx, ty)
        # Secondary tie-break: keep pressure on opponent (reduce opponent's distance to same target less).
        opp_dist = mhd(ox, oy, tx, ty)
        score = dist * 100 + (opp_dist - dist)
        if score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]