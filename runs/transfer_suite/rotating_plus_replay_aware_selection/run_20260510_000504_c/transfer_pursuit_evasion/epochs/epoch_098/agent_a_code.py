def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("escape" in role) or ("runner" in role) or ("flee" in role)

    INF = 10**9
    start = (ox, oy) if not is_evader else (ox, oy)
    # For evader, we still BFS from opponent to measure separation; for pursuer, BFS from opponent to measure catch distance.
    dist = [[INF] * h for _ in range(w)]
    if start not in obstacles:
        qx, qy = [start[0]], [start[1]]
        dist[start[0]][start[1]] = 0
        head = 0
        steps = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        while head < len(qx):
            x, y = qx[head], qy[head]
            head += 1
            nd = dist[x][y] + 1
            for dx, dy in steps:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):  # engine would clamp by staying; treat as invalid
            continue
        if (nx, ny) in obstacles:
            continue
        d = dist[nx][ny] if dist[nx][ny] < INF else abs(nx - ox) + abs(ny - oy)
        # pursuer: minimize separation; evader: maximize separation
        man = abs(nx - ox) + abs(ny - oy)
        score = d if not is_evader else -d
        # tie-break: avoid stepping into opponent-adjacent squares when evading; for pursuer, prefer approach in both metrics
        opp_adj = max(abs(nx - ox), abs(ny - oy))
        if is_evader:
            score += 0.05 * opp_adj + 0.001 * man
        else:
            score += -0.05 * opp_adj - 0.001 * man
        if best is None or (score < best_score if not is_evader else score > best_score):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]