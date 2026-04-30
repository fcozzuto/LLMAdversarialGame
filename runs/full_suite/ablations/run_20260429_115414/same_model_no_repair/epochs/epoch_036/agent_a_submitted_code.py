def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = {(p[0], p[1]) for p in obstacles}

    moves8 = [(-1, -1), (0, -1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    moves4n = [(-1,0),(1,0),(0,-1),(0,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def bfs_dist(start):
        INF = 10**9
        dist = [[INF]*h for _ in range(w)]
        if not inb(start[0], start[1]) or start in blocked:
            return dist
        from_pos = [start]
        dist[start[0]][start[1]] = 0
        i = 0
        while i < len(from_pos):
            x, y = from_pos[i]
            i += 1
            nd = dist[x][y] + 1
            for dx, dy in moves8:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in blocked and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    from_pos.append((nx, ny))
        return dist

    def prox_to_obstacle(x, y):
        s = 0
        for dx, dy in moves4n:
            nx, ny = x + dx, y + dy
            if (nx, ny) in blocked:
                s += 1
        return s

    self_dist = bfs_dist((sx, sy))
    opp_dist = bfs_dist((ox, oy))

    best_target = None
    best_score = -10**18
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in blocked:
            continue
        sd = self_dist[rx][ry]
        od = opp_dist[rx][ry]
        if sd >= 10**8 and od >= 10**8:
            continue
        # Prefer targets opponent can reach sooner than us? actually we want our advantage: od - sd higher.
        # Penalize proximity to obstacles to avoid traps/dead-ends.
        val = (od - sd) - 0.35 * prox_to_obstacle(rx, ry)
        # Also lightly prefer targets that are not too far away from us to secure them.
        val -= 0.05 * sd
        if val > best_score:
            best_score = val
            best_target = (rx, ry)

    if best_target is None:
        return [0, 0]

    tx, ty = best_target

    def clamp_move(dx, dy):
        if dx < -1: dx = -1
        if dx > 1: dx = 1
        if dy < -1: dy = -1
        if dy > 1: dy = 1
        return [dx, dy]

    best_move = [0, 0]
    best_move_val = -10**18

    for dx, dy in moves8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        sd_after = self_dist[tx][ty] - (self_dist[nx][ny] - self_dist[sx][sy])
        # If BFS values are INF, keep safe fallback
        if self_dist[nx][ny] >= 10**8:
            sd_after = 10**9
        # Estimate local advantage after moving closer.
        my = self_dist[tx][ty] if self_dist[tx][ty] < 10**8 else sd_after
        my = self_dist[tx][ty]
        if my >= 10**8:
            my = sd_after
        gain = (opp_dist[tx][ty] - my) if opp_dist[tx][ty] < 10**8 else -10**6
        # Avoid stepping near obstacles.
        avoid = prox_to_obstacle(nx, ny)
        # Also ensure progress toward target.
        progress = max(abs(tx