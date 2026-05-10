def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    seen = set()
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles and (x, y) not in seen:
                seen.add((x, y))
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_val = -10**18
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            nx, ny = sx, sy

        best_res_val = -10**18
        for rx, ry in resources:
            self_d = cheb((nx, ny), (rx, ry))
            opp_d = cheb((ox, oy), (rx, ry))
            # Win-the-race margin first; finish sooner second.
            val = (opp_d - self_d) * 100 - self_d - abs(self_d - opp_d) * 0.5
            if val > best_res_val:
                best_res_val = val

        # Opponent tends to sweep across rows: reduce mismatch in y to contest their next sweep line.
        row_bias = -abs(ny - oy) * 0.25
        total = best_res_val + row_bias

        if total > best_val:
            best_val = total
            best_move = [dx if (nx != sx or ny != sy) else 0, dy if (nx != sx or ny != sy) else 0]
            if best_move == [0, 0] and (dx != 0 or dy != 0):
                best_move = [dx, dy]

    if not isinstance(best_move[0], int):
        best_move = [int(best_move[0]), int(best_move[1])]
    return [max(-1, min(1, best_move[0])), max(-1, min(1, best_move[1]))]