def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    self_role = observation.get("self_role", "") or ""
    is_evader = ("evader" in self_role.lower()) or ("runner" in self_role.lower())

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves.sort()

    obst_list = list(obstacles)

    def dist_to_obst(x, y):
        if not obst_list:
            return 8
        best = 10**9
        for ax, ay in obst_list:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
        return best

    best_m = [0, 0]
    best_v = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = abs(nx - ox) + abs(ny - oy)
        dob = dist_to_obst(nx, ny)
        edge = min(nx, ny, (w - 1) - nx, (h - 1) - ny)
        edge_pen = -edge  # avoid hugging edges unless necessary

        if is_evader:
            v = 1000 * d + 5 * dob + 0.5 * edge_pen
        else:
            v = -1000 * d + 3 * dob + 0.5 * edge_pen

        if best_v is None or (v > best_v) or (v == best_v and [dx, dy] < best_m):
            best_v = v
            best_m = [dx, dy]

    return best_m