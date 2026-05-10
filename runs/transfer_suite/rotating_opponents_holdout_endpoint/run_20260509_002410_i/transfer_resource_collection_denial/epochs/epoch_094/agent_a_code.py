def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
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

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    best = None
    best_val = -10**18
    # Find a resource where we can arrive no later than opponent; otherwise nearest by distance.
    for rx, ry in resources:
        d_me = man(sx, sy, rx, ry)
        d_opp = man(ox, oy, rx, ry)
        if d_me <= d_opp:
            val = (d_opp - d_me) * 1000 - d_me
        else:
            val = -(d_me * 10 + (d_me - d_opp))  # penalize being behind
        if val > best_val:
            best_val = val
            best = (rx, ry)

    tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = 10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        d1 = man(nx, ny, tx, ty)
        # Prefer moves that keep/increase our chance to arrive first.
        d_me_next = d1
        d_opp_next = man(ox, oy, tx, ty)
        lead = d_opp_next - d_me_next
        # Score: primary distance to target, secondary lead, tertiary avoid staying if equal.
        score = d1 * 1000 - lead * 5 + (1 if (dx == 0 and dy == 0) else 0)
        if score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]