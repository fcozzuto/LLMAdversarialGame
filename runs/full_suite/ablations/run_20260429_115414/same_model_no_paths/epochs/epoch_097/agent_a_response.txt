def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def bfs_from(src):
        INF = 10**6
        dist = [[INF] * h for _ in range(w)]
        x0, y0 = src
        if (x0, y0) in obstacles:
            return dist
        dist[x0][y0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    d_self = bfs_from((sx, sy))
    d_opp = bfs_from((ox, oy))

    best_targets = []
    best_score = -10**9
    for rx, ry in resources:
        a = d_self[rx][ry]
        b = d_opp[rx][ry]
        if a >= 10**6:
            continue
        score = (b - a) * 10 - a  # win race and then be closer sooner
        if score > best_score:
            best_score = score
            best_targets = [((rx, ry), score, a, b)]
        elif score == best_score:
            best_targets.append(((rx, ry), score, a, b))
    target = best_targets[0][0]
    tx, ty = target

    # Move selection: minimize distance to chosen target; secondary: improve race margin
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            ds = d_self[nx][ny]
            dt = d_self[nx][ny]  # not used directly, but keep deterministic structure
            our_to_t = bfs_from((nx, ny))[tx][ty] if False else d_self[tx][ty]  # placeholder avoided by branch
            # Avoid per-move BFS: use precomputed dist to target from current/approx via direct dist
            # Since graph edges are uniform, use Chebyshev as tiebreaker when precomputed lacks.
            our_to_t = d_self[tx][ty]  # fallback constant bias (keeps determinism); we override with direct move tiebreaker below
            our_step_to_t = max(abs(nx - tx), abs(ny - ty))
            opp_to_t = d_opp[tx][ty]
            race = opp_to_t - our_step_to_t
            candidates.append((our_step_to_t, -race, dx, dy))
    candidates.sort()
    _, _, dx, dy = candidates[0] if candidates else (0, 0, 0, 0)
    return [int(dx), int(dy)]