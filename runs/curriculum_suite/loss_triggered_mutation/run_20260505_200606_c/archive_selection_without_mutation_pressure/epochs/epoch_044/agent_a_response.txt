def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a target we can contest: highest (opp_dist - self_dist), prefer closer-to-you if tied.
    best_r = resources[0]
    best_adv = -10**18
    for rx, ry in resources:
        d_self = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        adv = d_opp - d_self
        if adv > best_adv or (adv == best_adv and (d_self < cheb(sx, sy, best_r[0], best_r[1]))):
            best_adv = adv
            best_r = (rx, ry)
    tx, ty = best_r

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_next = cheb(nx, ny, tx, ty)
        d_opp_next = cheb(nx, ny, ox, oy)

        # Drive to contested target while keeping some separation from opponent.
        score = (-d_next) + 0.15 * d_opp_next

        # Extra nudge: avoid moving into cells where opponent can be closer to the same target than we are.
        d_opp_to_target = cheb(ox, oy, tx, ty)
        if cheb(nx, ny, tx, ty) > d_opp_to_target:
            score -= 2.5

        # Deterministic tie-break
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]