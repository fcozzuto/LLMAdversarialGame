def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    INF = 10**9
    def bfs(start):
        dist = [[INF] * h for _ in range(w)]
        x0, y0 = start
        if not valid(x0, y0):
            return dist
        dist[x0][y0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    distS = bfs((sx, sy))
    distO = bfs((ox, oy))

    res_set = set(tuple(p) for p in resources)
    best_resource = None
    best_key = None
    for rx, ry in res_set:
        ds = distS[rx][ry]
        if ds >= INF: 
            continue
        do = distO[rx][ry]
        # Prefer resources we can reach first; break ties by being closer, then by deterministic coordinate order
        key = (0 if ds < do else 1, ds - do, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_resource = (rx, ry)

    rx, ry = best_resource if best_resource is not None else (sx, sy)

    # Choose move that improves arrival at target while denying opponent progress to that target
    best = (-INF, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds_n = distS[nx][ny]
        do_target = distO[rx][ry]
        ds_target_now = distS[rx][ry]  # constant for this turn
        # After moving, approximate time to reach target using BFS distance from new position
        ds_to_target = distS[rx][ry] if (nx == sx and ny == sy) else distS[rx][ry]
        # We want to use distance from new position to target; compute by reusing BFS? cheap: local BFS if needed.
        # Instead approximate using triangle: if target not reachable from new, penalize; else use dist from new to target via BFS from new.
        # Keep deterministic and still fast: only if close competition; otherwise use greedy.
        # Deterministic local BFS only when it's likely helpful (resources exist).
        if best_resource is not None:
            # local BFS from candidate for accurate ds_to_target
            distN = bfs((nx, ny))
            ds_to_target = distN[rx][ry]
        if ds_to_target >= INF:
            continue

        # Advantage score: smaller ds_to_target is better; larger opponent reach time is better.
        # Also immediate pickup gets large reward.
        pickup = 1 if (nx, ny) in res_set else 0
        opp_to_target = distO[rx][ry]
        opp_adv = opp_to_target - ds_to_target  # positive means we can arrive earlier
        # Prefer also to not get too close to opponent unless it helps us grab first.
        opp_dist = max(abs(nx - ox), abs(ny - oy))
        score = 0
        score += 10000 * pickup
        score += 200 * (1 if ds_to_target < opp_to_target else 0)
        score += 50 * opp_adv
        score += opp_dist
        # Small tie-breaker: deterministic ordering by coordinates
        score += (-(nx * w + ny)) * 1e-6

        if score > best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]]