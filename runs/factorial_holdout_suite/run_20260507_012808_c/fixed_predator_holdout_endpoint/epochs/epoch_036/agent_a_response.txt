def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Deterministic move evaluation: pick next step that maximizes expected "lead"
    # after taking into account opponent reachability; add a small tie-break
    # encouraging forward progress from our current position.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_score = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        my_next = (nx, ny)

        # Choose best resource under this next position.
        best_res_score = None
        best_res = None
        for rx, ry in resources:
            res = (rx, ry)
            my_d = cheb(my_next, res)
            op_d = cheb((ox, oy), res)
            lead = op_d - my_d  # positive means we are closer/equal than opponent
            # progress bias: prefer reducing distance from current position
            cur_d = cheb((sx, sy), res)
            progress = cur_d - my_d  # positive if we move closer
            score = (lead * 10) + progress  # scale lead strongly
            if best_res_score is None or score > best_res_score:
                best_res_score = score
                best_res = res

        # If tie, pick move with smaller distance to that chosen resource (more committed)
        commit = cheb(my_next, best_res) if best_res is not None else 0
        total = best_res_score if best_res_score is not None else -10**9

        if best_score is None or total > best_score or (total == best_score and commit < cheb((best_move[0] + sx, best_move[1] + sy), best_res)):
            best_score = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]