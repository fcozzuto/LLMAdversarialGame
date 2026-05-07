def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    occ = set((x, y) for x, y in obstacles)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Select target resource: prioritize where we arrive earlier; otherwise closest.
    best_r = resources[0]
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        lead = od - sd  # positive => we are ahead
        behindness = sd - od  # positive => we are behind
        key = (abs(behindness), -lead, sd, abs(rx - (w - 1) // 2) + abs(ry - (h - 1) // 2), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)
    tx, ty = best_r

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in occ:
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        lead2 = nod - nsd
        # Prefer decreasing distance; also strongly prefer moves that keep/achieve lead.
        score = (nsd, -lead2, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move