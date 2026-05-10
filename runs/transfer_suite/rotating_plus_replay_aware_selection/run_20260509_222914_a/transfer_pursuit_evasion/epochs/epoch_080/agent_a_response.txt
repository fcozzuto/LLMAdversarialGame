def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    i_am_evader = ("evader" in role) or ("runner" in role) or ("escape" in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # One-step minimax estimate: assume opponent moves optimally for its role.
    def best_opp_move(ex2, ey2):
        best = None
        best_val = None
        for dx, dy in moves:
            nx, ny = ox + dx, oy + dy
            if not valid(nx, ny):
                continue
            d = dist(ex2, ey2, nx, ny)
            val = d if i_am_evader else -d  # if we are evader, opponent is pursuer -> maximize distance for itself? actually pursuer minimizes distance
            if i_am_evader:
                # opponent pursues: minimize distance to us
                val = -d
            else:
                # opponent evades: maximize distance from us
                val = d
            if best_val is None or val > best_val or (val == best_val and (dx, dy) < best):
                best_val = val
                best = (dx, dy)
        return best if best is not None else (0, 0)

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if i_am_evader:
            # we want to maximize opponent's best response distance
            odx, ody = best_opp_move(nx, ny)
            enx, eny = ox + odx, oy + ody
            val = dist(nx, ny, enx, eny)
        else:
            # we want to minimize opponent's best response distance
            odx, ody = best_opp_move(nx, ny)
            enx, eny = ox + odx, oy + ody
            val = -dist(nx, ny, enx, eny)
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]