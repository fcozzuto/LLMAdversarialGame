def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist8(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def nearest_from(pos):
        px, py = pos
        best = resources[0]
        bd = dist8((px, py), best)
        for r in resources[1:]:
            d = dist8((px, py), r)
            if d < bd:
                bd = d
                best = r
        return best, bd

    opp_tgt, opp_d = nearest_from((ox, oy))
    opp_adj = None
    for dx, dy in moves:
        nx, ny = ox + dx, oy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            if dist8((nx, ny), opp_tgt) <= opp_d:
                opp_adj = (nx, ny)
                break

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        my_tgt, my_d = nearest_from((nx, ny))
        score = -my_d

        # Contest opponent target: prefer moves that reduce our distance to their target
        my_to_opp = dist8((nx, ny), opp_tgt)
        score += 1.6 * (opp_d - my_to_opp)

        # Block: if we can land on/adjacent to their next greedy-adjacent region, boost
        if opp_adj is not None:
            if (nx, ny) == opp_adj:
                score += 12.0
            elif dist8((nx, ny), opp_adj) <= 1:
                score += 4.0

        # Resource safety: avoid stepping onto cells adjacent to obstacles less (deterministic mild preference)
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obstacles:
                    adj_obs += 1
        score -= 0.08 * adj_obs

        # Deterministic tie-breaker: keep move with smallest lexicographic (dx,dy)
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]