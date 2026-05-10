def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", None) or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", None) or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if resources:
            # Choose moves that create the largest advantage over opponent for at least one resource.
            best_adv = None
            best_adv_dist = None
            best_our_near = None
            for r in resources:
                our_d = dist((nx, ny), r)
                opp_d = dist((ox, oy), r)
                adv = opp_d - our_d
                if best_adv is None or adv > best_adv or (adv == best_adv and our_d < best_adv_dist):
                    best_adv = adv
                    best_adv_dist = our_d
                if best_our_near is None or our_d < best_our_near:
                    best_our_near = our_d

            if best_adv > 0:
                # Strongly pursue resources we are better positioned for.
                key = (-best_adv, best_adv_dist, dist((nx, ny), (ox, oy)))
            else:
                # If we're not well-positioned to win a contest, just reduce our nearest distance.
                key = (0, best_our_near, dist((nx, ny), (ox, oy)))
        else:
            # No resources visible: move to increase distance from opponent while staying safe.
            key = (0, dist((nx, ny), (ox, oy)), abs((nx + ny) - (sx + sy)))
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]