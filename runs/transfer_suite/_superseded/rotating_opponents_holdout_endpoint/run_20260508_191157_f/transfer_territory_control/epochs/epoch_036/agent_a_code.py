def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    self_terr = observation.get("self_territory") or []
    self_set = set()
    for x, y in self_terr:
        x, y = int(x), int(y)
        if inside(x, y):
            self_set.add((x, y))

    unclaimed = observation.get("unclaimed_cells") or []
    un_list = []
    for x, y in unclaimed:
        x, y = int(x), int(y)
        if inside(x, y):
            un_list.append((x, y))
    un_set = set(un_list)

    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def adj_to_self(cell):
        x, y = cell
        for dx, dy in neigh8:
            if dx == 0 and dy == 0:
                continue
            if (x + dx, y + dy) in self_set:
                return True
        return False

    best = None
    best_score = None
    for dx, dy in neigh8:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in blocked:
            continue
        if not un_list:
            score = dist((nx, ny), (ox, oy))  # just stay safe
        else:
            dmin = 10**9
            for tx, ty in un_list:
                dd = dist((nx, ny), (tx, ty))
                if dd < dmin:
                    dmin = dd
            score = -dmin
            if (nx, ny) in un_set:
                score += 1000
            if adj_to_self((nx, ny)):
                score += 100
        if best is None or score > best_score:
            best = [dx, dy]
            best_score = score

    if best is None:
        return [0, 0]
    return best