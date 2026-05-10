def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    selfT = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    opT = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    unT = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    nbrs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def adj_count(x, y, S):
        c = 0
        for dx, dy in nbrs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in S:
                c += 1
        return c

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_val = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        in_self = (nx, ny) in selfT
        in_op = (nx, ny) in opT
        in_un = (nx, ny) in unT

        a_self = adj_count(nx, ny, selfT)
        a_op = adj_count(nx, ny, opT)
        a_un = adj_count(nx, ny, unT)

        dist_op = manh(nx, ny, ox, oy)
        near_op = 8 - min(8, dist_op)  # closer => larger

        val = 0
        if in_op:
            val += 220 + 10 * a_self - 2 * a_op - dist_op
        elif in_un:
            val += 70 + 18 * a_self + 6 * a_un - 1 * a_op + near_op
        elif in_self:
            val += 25 + 22 * a_self - 5 * a_op - 0.5 * dist_op
        else:
            val += 5 + 6 * a_self + 2 * a_un - 3 * a_op

        # Prefer progressing away from "entrapment": avoid staying adjacent-heavy to opponent unless capturing
        if not in_op:
            val -= 8 * a_op

        # Deterministic tie-breaker: prefer moves that reduce distance to our nearest frontier-ish cell
        if val > best_val or (val == best_val and (manh(nx, ny, ox, oy), dx, dy) < (best[0], best[1], best[2])):
            best_val = val
            best = (manh(nx, ny, ox, oy), dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]