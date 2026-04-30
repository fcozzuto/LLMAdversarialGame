def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obst = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obst or not inb(x, y)

    # If standing on a resource, collect.
    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    INF = 10**9
    def bfs(start):
        x0, y0 = start
        if blocked(x0, y0):
            return None
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        qx, qy = [x0], [y0]
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if not blocked(nx, ny) and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    if not resources:
        return [0, 0]

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd is None or opd is None:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        md = myd[ry][rx]
        od = opd[ry][rx]
        if md >= INF or od >= INF:
            continue
        # Prefer resources where we beat the opponent, then closer for us, then farther from them.
        key = (md - od, md, -(abs(ox - rx) + abs(oy - ry)))
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    if best is None:
        return [0, 0]
    tx, ty = best

    # Choose one move that reduces our distance to target; tie-break by increasing our distance from opponent.
    best_move = [0, 0]
    best_md = myd[ty][sx]
    best_sep = abs(ox - sx) + abs(oy - sy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        if myd[ny][nx] >= INF:
            continue
        # Ensure this move actually progresses toward target using precomputed distances.
        # If unreachable, ignore (but already filtered above).
        my_to_target = myd[ty][nx]
        if my_to_target < best_md:
            best_md = my_to_target
            best_sep = abs(ox - nx) + abs(oy - ny)
            best_move = [dx, dy]
        elif my_to_target == best_md:
            sep = abs(ox - nx) + abs(oy - ny)
            if sep > best_sep:
                best_sep = sep
                best_move = [dx, dy]
            elif sep == best_sep:
                # Deterministic tie-break by preferred direction order
                if (dx, dy) < (best_move[0], best_move[1]):
                    best_move = [dx, dy]

    return best_move