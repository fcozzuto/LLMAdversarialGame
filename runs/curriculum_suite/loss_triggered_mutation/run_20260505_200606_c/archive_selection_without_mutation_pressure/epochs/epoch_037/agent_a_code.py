def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Deterministic target selection with mild diversification by turn parity
    parity = observation.get("turn_index", 0) & 1
    best = None
    best_val = -10**18
    for rx, ry in resources:
        d_opp = cheb(ox, oy, rx, ry)
        d_self = cheb(sx, sy, rx, ry)
        # Prefer resources closer to us than opponent; tie-break by urgency and parity
        val = (d_opp - d_self) * 100 + (-(d_self + (rx + ry) % 2) if parity == 0 else -(d_self))
        if val > best_val or (val == best_val and (rx, ry) < best):
            best_val = val
            best = (rx, ry)
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_now_opp = cheb(ox, oy, tx, ty)
        # One-step lookahead score: closer to target, and reduce opponent's relative advantage
        score = (d_now_opp - d_self) * 120 - d_self
        # If opponent is nearer to the target, bias toward moves that block nearby resources deterministically
        if d_now_opp < cheb(sx, sy, tx, ty):
            # add small penalty for moving away from the center line between us and opponent
            score -= cheb(nx, ny, ox, oy) * 2
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]