def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = {(p[0], p[1]) for p in obstacles_list}

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    INF = 10**9

    def bfs(start):
        x0, y0 = start
        dist = [[INF] * w for _ in range(h)]
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return dist
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    opd = bfs((ox, oy))
    best_move = (0, 0)
    best_val = -INF

    def val_from_cell(cell):
        cx, cy = cell
        md = bfs((cx, cy))
        best_adv = -INF
        any_ok = False
        for rx, ry in resources:
            mdv = md[ry][rx]
            odv = opd[ry][rx]
            if mdv >= INF or odv >= INF:
                continue
            any_ok = True
            adv = odv - mdv
            if adv > best_adv:
                best_adv = adv
        if any_ok:
            return best_adv
        # No reachable resources: drift to center, but slightly away from opponent
        cx0, cy0 = (w - 1) / 2.0, (h - 1) / 2.0
        dcen = max(abs(cx - cx0), abs(cy - cy0