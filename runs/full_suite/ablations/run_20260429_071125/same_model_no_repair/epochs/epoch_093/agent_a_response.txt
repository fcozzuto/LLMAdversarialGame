def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        my_d = min(dist((nx, ny), r) for r in resources)
        opp_d = min(dist((ox, oy), r) for r in resources)
        # Higher score is better: win-the-race on distance, then closer absolute, then deterministic tie-break
        score = (opp_d - my_d) * 1000 - my_d
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # tie-break: prefer smallest my_d then lex on move
            if my_d < min(dist((sx + best_move[0], sy + best_move[1]), r) for r in resources):
                best_move = (dx, dy)
            elif my_d == min(dist((sx + best_move[0], sy + best_move[1]), r) for r in resources) and (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]