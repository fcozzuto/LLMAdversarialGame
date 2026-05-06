def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal_moves(x, y):
        out = []
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                out.append((dx, dy, nx, ny))
        if not out:
            out = [(0, 0, x, y)]
        return out

    if not resources:
        return [0, 0]

    # Predict opponent greedy 1-step towards their nearest resource.
    opp_moves = legal_moves(ox, oy)
    best_opp_r = None
    best_opp_d = None
    for rx, ry in resources:
        d = cheb(ox, oy, rx, ry)
        if best_opp_d is None or d < best_opp_d:
            best_opp_d = d
            best_opp_r = (rx, ry)

    # If no target, stay.
    if best_opp_r is None:
        return [0, 0]
    tx, ty = best_opp_r

    # Compute opponent next position by greedy towards tx,ty.
    best_opp_next = (ox, oy)
    best_opp_next_d = None
    for dx, dy, nx, ny in opp_moves:
        d = cheb(nx, ny, tx, ty)
        if best_opp_next_d is None or d < best_opp_next_d:
            best_opp_next_d = d
            best_opp_next = (nx, ny)
    o2x, o2y = best_opp_next

    # Evaluate our move by how much closer we are to the opponent-target after their step,
    # and secondarily by general advantage vs all resources.
    best_score = None
    best_move = (0, 0)
    for dx, dy, nx, ny in legal_moves(sx, sy):
        # primary: race against their likely target
        adv_primary = cheb(o2x, o2y, tx, ty) - cheb(nx, ny, tx, ty)

        # secondary: avoid giving them strong options (maximize best advantage we have)
        best_adv = -10**9
        for rx, ry in resources:
            a = cheb(o2x, o2y, rx, ry) - cheb(nx, ny, rx, ry)
            if a > best_adv:
                best_adv = a

        # small preference for moving toward any resource deterministically
        nearest_my = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        score = (adv_primary * 1000) + (best_adv) - nearest_my * 0.01

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]