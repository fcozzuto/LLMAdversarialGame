def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]
    if not resources:
        return [0, 0]

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def bfs_dist(start):
        INF = 10**9
        dist = [[INF] * gh for _ in range(gw)]
        if (start[0], start[1]) in obstacles:
            return dist
        q = [(start[0], start[1])]
        dist[start[0]][start[1]] = 0
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            d = dist[x][y] + 1
            for dx, dy in moves[1:]:  # exclude stay for BFS spreading
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and d < dist[nx][ny]:
                    dist[nx][ny] = d
                    q.append((nx, ny))
        return dist

    sd = bfs_dist((sx, sy))
    od = bfs_dist((ox, oy))

    best = None
    best_key = None
    for rx, ry in resources:
        our = sd[rx][ry]
        opp = od[rx][ry]
        if our >= 10**8 and opp >= 10**8:
            continue
        # Prefer reachable sooner; if contested, prioritize deny when opponent can reach first
        adv = (our - 0.85 * opp) + (0.05 * abs(rx - ox) + 0.05 * abs(ry - oy))
        # Prefer smaller our distance overall to avoid deadlocks
        key = (round(adv, 6), our + opp * 0.001)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry, our, opp)

    if best is None:
        return [0, 0]
    tx, ty, ourd, oppd = best

    # If opponent is significantly closer, try to "shadow" by moving toward the resource they likely contest
    # using the local best-next-step from our distance map (still deterministic and obstacle-safe).
    best_step = [0, 0]
    best_step_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        our_next = sd[nx][ny]
        # choose step that reduces distance to target primarily; tie-break toward improving our advantage
        step_score = (our_next - 0.7 * od[tx][ty], abs(nx - tx) + abs(ny - ty), -abs(nx - ox) - abs(ny - oy))
        if best_step_score is None or step_score < best_step_score:
            best_step_score = step_score
            best_step = [dx, dy]

    return best_step