def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evader" in sr) or ("runner" in sr) or (("pursuer" not in sr) and ("evader" in orr))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def bfs_dist(start, target):
        if start == target:
            return 0
        if not inside(*start) or not inside(*target):
            return 10**9
        q = [start]
        head = 0
        dist = {start: 0}
        while head < len(q):
            x, y = q[head]
            head += 1
            nd = dist[(x, y)] + 1
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if inside(nx, ny) and (nx, ny) not in dist:
                        dist[(nx, ny)] = nd
                        if (nx, ny) == target:
                            return nd
                        q.append((nx, ny))
        return 10**9

    opp = (ox, oy)
    best_move = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            nx, ny = sx, sy
        dist_to_opp = bfs_dist((nx, ny), opp)
        man = abs(nx - ox) + abs(ny - oy)
        # Deterministic tie-break: prefer smaller (dx,dy) lexicographically.
        val = (-dist_to_opp, man) if self_is_evader else (dist_to_opp, man)
        if best_val is None or val < best_val if not self_is_evader else val > best_val:
            best_val = val
            best_move = [int(dx), int(dy)]
        elif best_val is not None:
            if self_is_evader:
                if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
                    best_move = [int(dx), int(dy)]
            else:
                if val < best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
                    best_move = [int(dx), int(dy)]

    return best_move