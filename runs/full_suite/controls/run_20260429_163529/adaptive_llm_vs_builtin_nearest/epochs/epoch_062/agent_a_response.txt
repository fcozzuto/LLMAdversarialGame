def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    turn = int(observation.get("turn_index", 0) or 0)

    # Choose a target resource: prefer ones we can reach not much later than opponent.
    best_target = resources[0]
    best_val = None
    for r in resources:
        rx, ry = r
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # If we're closer, lower; if opponent closer, penalize.
        val = myd * 3 + max(0, myd - opd) * 6 + (rx + ry) % 2
        if best_val is None or val < best_val:
            best_val = val
            best_target = r

    tx, ty = best_target

    # Pick move that minimizes distance to target while avoiding obstacles/out-of-bounds.
    best_moves = []
    best_dist = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, tx, ty)
        # Small deterministic tie-breakers: also avoid approaching opponent too much.
        opp_close = cheb(nx, ny, ox, oy)
        score = d * 10 - opp_close
        if best_dist is None or score < best_dist:
            best_dist = score
            best_moves = [(dx, dy)]
        elif score == best_dist:
            best_moves.append((dx, dy))

    # If all moves invalid (shouldn't happen), stay.
    if not best_moves:
        return [0, 0]

    # Deterministic selection among ties using turn_index parity.
    idx = turn % len(best_moves)
    return [int(best_moves[idx][0]), int(best_moves[idx][1])]