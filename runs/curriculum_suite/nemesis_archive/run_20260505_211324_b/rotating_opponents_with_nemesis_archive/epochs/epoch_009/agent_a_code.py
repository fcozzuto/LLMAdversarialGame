def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = p
            obstacles.add((x, y))
        except Exception:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = r
            resources.append((x, y))
        except Exception:
            pass

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = [0, 0]
    best_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        if not resources:
            key = (0, abs(nx - ox) + abs(ny - oy), dx, dy)
        else:
            # Choose a resource that maximizes how much closer we are than the opponent.
            # key: (best_lead, -our_dist, -opp_dist, rx, ry)
            best_for_move = None
            for rx, ry in resources:
                our_d = manh(nx, ny, rx, ry)
                op_d = manh(ox, oy, rx, ry)
                lead = op_d - our_d
                cand = (lead, -our_d, -op_d, rx, ry)
                if best_for_move is None or cand > best_for_move:
                    best_for_move = cand
            # key for move prefers larger lead, then smaller our_d, then lexicographic move
            key = (-best_for_move[0], best_for_move[1], best_for_move[2], best_for_move[3], best_for_move[4], dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move