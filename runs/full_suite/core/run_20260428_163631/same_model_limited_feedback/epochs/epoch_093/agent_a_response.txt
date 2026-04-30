def choose_move(observation):
    x, y = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation["obstacles"]
    resources = observation["resources"]
    obs_set = set((ox, oy) for ox, oy in obstacles)
    res_set = set((rx, ry) for rx, ry in resources)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def closest_res_dist(nx, ny):
        best = None
        for rx, ry in resources:
            d = abs(rx - nx) + abs(ry - ny)
            if best is None or d < best:
                best = d
        return best if best is not None else 999999

    moves = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    # Deterministic tie-breaking preference: toward increasing x, then increasing y, then staying.
    moves = sorted(moves, key=lambda m: (m[0], m[1]))

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        d = closest_res_dist(nx, ny)
        # Strongly prefer moving onto a resource.
        score = -d
        if (nx, ny) in res_set:
            score += 10000
        # Mild preference for moves that reduce distance more than others.
        # Also gently prefer progressing toward board center to avoid getting stuck near corners.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score -= 0.01 * (abs(nx - cx) + abs(ny - cy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]