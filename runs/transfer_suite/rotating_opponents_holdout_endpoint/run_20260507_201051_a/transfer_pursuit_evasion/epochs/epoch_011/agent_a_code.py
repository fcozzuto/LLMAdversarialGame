def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obs.add((int(x), int(y)))
        except Exception:
            pass

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    is_evader = str(observation.get("self_role", "")).lower() == "evader"

    # BFS distances from opponent (or pursuer/evader distance perspective doesn't matter; we use it for greedy).
    srcx, srcy = ox, oy
    dist = [[-1] * w for _ in range(h)]
    if free(srcx, srcy):
        q = [(srcx, srcy)]
        dist[srcy][srcx] = 0
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[y][x] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if free(nx, ny) and dist[ny][nx] == -1:
                    dist[ny][nx] = nd
                    q.append((nx, ny))

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = dist[ny][nx]
        if d == -1:
            d = 10**9  # unreachable
        # Pursuer minimizes distance; evader maximizes distance.
        val = d if not is_evader else -d
        if best is None or val > best_val:
            best_val = val
            best = (dx, dy)
        elif best is not None and val == best_val:
            # deterministic tie-break: prefer fewer dx, then fewer dy, then 0 move
            bx, by = best
            if (abs(dx), abs(dy), dx, dy) < (abs(bx), abs(by), bx, by):
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]