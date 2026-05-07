def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set()
    for p in observation.get("obstacles", []):
        obstacles.add((p[0], p[1]))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_key = None

    # Evaluate each candidate move by best guaranteed advantage over all resources
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        chosen = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach earlier; then maximize opponent delay; then minimize our distance; then stable tie
            k = (0 if ds < do else 1, -(do - ds), ds, 7 * ry + rx)
            if chosen is None or k < chosen:
                chosen = k
        if chosen is None:
            continue
        # From all resources-optimized picks, choose move that most improves (reach earlier, then reduce our dist, then increase opp dist)
        final_key = (chosen[0], chosen[1], chosen[2], chosen[3], dx, dy)
        if best_key is None or final_key < best_key:
            best_key = final_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]