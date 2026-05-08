def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    inf = 10**9

    def bfs(st):
        dist = [[inf] * gh for _ in range(gw)]
        x0, y0 = st
        if 0 <= x0 < gw and 0 <= y0 < gh:
            dist[x0][y0] = 0
        qx, qy, head = [x0], [y0], 0
        while head < len(qx):
            x, y = qx[head], qy[head]
            head += 1
            d2 = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obstacles:
                    if d2 < dist[nx][ny]:
                        dist[nx][ny] = d2
                        qx.append(nx)
                        qy.append(ny)
        return dist

    sd = bfs((sx, sy))
    od = bfs((ox, oy))

    best_res = None
    best_val = -10**18
    for rx, ry in resources:
        ds = sd[rx][ry]
        if ds >= inf:
            continue
        do = od[rx][ry]
        if do >= inf:
            do = 10**6
        # Prefer resources where we are closer than opponent, and closer overall
        val = (do - ds) * 1000 - ds + (rx - 0.5 * (gw - 1)) * 0 - (ry - 0.5 * (gh - 1)) * 0
        if val > best_val:
            best_val = val
            best_res = (rx, ry)

    tx, ty = best_res if best_res is not None else (sx, sy)

    # Move one step maximizing progress toward target while staying valid
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh) or (nx, ny) in obstacles:
            continue
        # If opponent is also threatening the target, slightly prefer paths that reduce opponent advantage
        score = -sd[nx][ny] * 10 + (od[tx][ty] - od[nx][ty] if 0 <= nx < gw and 0 <= ty < gh else 0) - abs(nx - tx) - abs(ny - ty) * 0.1
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    # If blocked (shouldn't happen), stay still deterministically
    if best_score == -10**18:
        return [0, 0]
    return best_move