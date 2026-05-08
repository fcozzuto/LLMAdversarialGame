def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    opp_neighbors = []
    for dx, dy in dirs:
        px, py = ox + dx, oy + dy
        if inb(px, py):
            opp_neighbors.append((px, py))

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d2 = dist2(nx, ny, ox, oy)
        if opp_neighbors:
            mobility = 0
            min_to_opp_option = None
            for px, py in opp_neighbors:
                mobility += 1
                dd = dist2(nx, ny, px, py)
                if min_to_opp_option is None or dd < min_to_opp_option:
                    min_to_opp_option = dd
        else:
            mobility = 0
            min_to_opp_option = dist2(nx, ny, ox, oy)

        val = d2 * 10 + mobility * 2 - int(min_to_opp_option)
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]