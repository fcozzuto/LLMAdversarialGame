def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            resources.append((r[0], r[1]))
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    best_move = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        opp_dist_from_new = man(nx, ny, ox, oy)

        best_r_key = None
        for rx, ry in resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            # Prefer resources where we are closer than the opponent
            val_diff = self_d - opp_d  # smaller is better
            r_key = (val_diff, self_d, opp_d)
            if best_r_key is None or r_key < best_r_key:
                best_r_key = r_key

        move_key = (best_r_key[0], best_r_key[1], -opp_dist_from_new, dx, dy)
        if best_move is None or move_key < best_move[0]:
            best_move = (move_key, dx, dy)

    return [best_move[1], best_move[2]]