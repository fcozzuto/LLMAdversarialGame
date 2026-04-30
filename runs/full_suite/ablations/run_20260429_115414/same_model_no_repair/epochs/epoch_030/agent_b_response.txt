def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = {(p[0], p[1]) for p in obstacles}
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    INF = 10**9

    def bfs(start):
        x0, y0 = start
        if not (0 <= x0 < w and 0 <= y0 < h) or (x0, y0) in obs:
            return None
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        qx, qy = [x0], [y0]
        i = 0
        while i < len(qx):
            x, y = qx[i], qy[i]
            i += 1
            nd = dist[y][x] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    if not resources:
        return [0, 0]

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd is None:
        return [0, 0]

    best = None
    best_key = None  # smaller is better
    for rx, ry in resources:
        dm = myd[ry][rx]
        if dm >= INF:
            continue
        do = opd[ry][rx] if opd is not None else INF
        # Prefer resources I can reach; maximize my advantage over opponent (minimize dm - do)
        key = (dm - do, dm, abs(rx - ox) + abs(ry - oy), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    # Step that maximizes my improvement and minimizes giving opponent advantage
    options = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        dcur = myd[sy][sx]
        dnext = myd[ny][nx]
        if dnext >= INF:
            continue
        # Heuristic: prefer smaller distance-to-target; if tie, prefer more "lead" over opponent at next cell
        my_improve = dcur - dnext
        do_next = opd[ny][nx] if opd is not None else INF
        opp_adv_risk = (do_next - dnext)  # smaller means opponent closer relative to me
        dist_to_target_next = abs(tx - nx) + abs(ty - ny)
        options.append((-(my_improve), dist_to_target_next, opp_adv_risk, dx, dy))

    if not options:
        return [0, 0]
    options.sort()
    return [int(options[0][3]), int(options[0][4])]