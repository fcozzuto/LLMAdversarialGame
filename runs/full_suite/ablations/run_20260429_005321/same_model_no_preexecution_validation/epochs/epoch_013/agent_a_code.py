def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    INF = 10**9

    def bfs(start):
        x0, y0 = start
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return [[INF] * w for _ in range(h)]
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    mydist = bfs((sx, sy))
    opdist = bfs((ox, oy))

    best_target = None
    best_val = -10**18
    for rx, ry in resources:
        md = mydist[ry][rx]; od = opdist[ry][rx]
        if md >= INF: 
            continue
        # Prioritize lead; slightly penalize long own travel.
        val = (od - md) * 100 - md
        if val > best_val:
            best_val = val
            best_target = (rx, ry)

    tx, ty = best_target if best_target is not None else (ox, oy)

    best_move = (0, 0); best_score = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Choose step that most improves relative claim on the target.
        ms = mydist[ny][nx] if mydist[ny][nx] < INF else INF
        os = opdist[ty][tx]  # constant-ish; keeps tie-breaking stable without recompute
        # Lower distance to target is good; also prefer positions where opponent is closer to its target.
        # But we don't know opponent's target precisely; approximate by reducing our distance to target primarily.
        dist_to_target = mydist[ty][tx]
        score = (dist_to_target - ms) * -1 + (nx - tx) * (nx - tx) * 0 + (ny - ty) * (ny - ty) * 0
        # Tie-break: avoid moving into squares with very high opponent distance advantage.
        score = score + (opdist[ny][nx] if opdist[ny][nx] < INF else INF) * 0.001
        if score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]