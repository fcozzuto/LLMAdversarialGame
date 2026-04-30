def choose_move(observation):
    W = observation["grid_width"]
    H = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H:
                moves.append((dx, dy))

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Resource distance terms
    if resources:
        res_list = [tuple(r) for r in resources]
        best_res_self = min(manh(x, y, rx, ry) for rx, ry in res_list)
        best_res_opp = min(manh(ox, oy, rx, ry) for rx, ry in res_list)
    else:
        best_res_self = 0
        best_res_opp = 0

    even_mode = (observation["turn_index"] % 2 == 0)

    best_move = (0, 0)
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if (nx, ny) in obstacles:
            score = -10**8
        else:
            if resources:
                dself = min(manh(nx, ny, rx, ry) for rx, ry in res_list)
                dopp = min(manh(ox, oy, rx, ry) for rx, ry in res_list)
                # Prefer being closer to resources than the opponent
                score = 6 * (dopp - dself) - 2 * dself
            else:
                score = 0
            # Strategic alternating objective to change policy when not improving
            d_op = manh(nx, ny, ox, oy)
            if even_mode:
                score += 0.4 * d_op  # keep spacing while grabbing resources
            else:
                score += -0.7 * d_op  # shadow / pressure opponent while still valuing resources
            # Mild center bias when tied
            score += -0.01 * manh(nx, ny, W // 2, H // 2)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]