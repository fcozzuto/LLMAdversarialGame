def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    # Target selection: pick resource where we are (or can become) ahead.
    if resources:
        best_r = None
        best_v = -10**18
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Strongly prefer resources where we are closer than opponent.
            v = (d_opp - d_me) * 100 - d_me
            # If opponent is currently much closer, penalize heavily.
            if d_opp + 1 < d_me:
                v -= 500
            if v > best_v:
                best_v = v
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        # No resources: drift towards center while keeping some distance from opponent.
        tx, ty = W // 2, H // 2

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_to = cheb(nx, ny, tx, ty)
        # Tie-break: increase distance from opponent to reduce contention.
        d_opp_next_approx = cheb(nx, ny, ox, oy)
        score = -d_to * 1000 + d_opp_next_approx
        # Small bias to keep moving deterministically toward target direction.
        if dx == 0 and dy == 0:
            score -= 1
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]