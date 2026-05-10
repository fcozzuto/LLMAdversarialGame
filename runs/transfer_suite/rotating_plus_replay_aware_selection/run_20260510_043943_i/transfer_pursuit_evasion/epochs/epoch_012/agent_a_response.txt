def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    role = observation.get("self_role", "pursuer")
    def dist2(x, y):
        dx = x - ox; dy = y - oy
        return dx * dx + dy * dy
    # 2-ply: assume opponent moves to optimize their objective (opposite of us)
    best_move = (0, 0); best_score = None; best_tie = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): 
            continue
        # Evaluate opponent response from (nx,ny) as our new position
        if role == "pursuer":
            # Opponent (evader) tries to maximize distance after they move
            worst = -1
            for odx, ody in moves:
                ex, ey = ox + odx, oy + ody
                if not valid(ex, ey): 
                    continue
                d = (nx - ex) * (nx - ex) + (ny - ey) * (ny - ey)
                if d > worst: worst = d
            score = -worst
            tie = (abs(dx) + abs(dy), -dist2(nx, ny))  # prefer movement and getting closer
        else:
            # Opponent (pursuer) tries to minimize distance after they move
            best = 10**18
            for odx, ody in moves:
                ex, ey = ox + odx, oy + ody
                if not valid(ex, ey):
                    continue
                d = (nx - ex) * (nx - ex) + (ny - ey) * (ny - ey)
                if d < best: best = d
            score = best
            tie = (abs(dx) + abs(dy), dist2(nx, ny))  # prefer movement and staying far
        if best_score is None or score > best_score or (score == best_score and tie > best_tie):
            best_score = score; best_tie = tie; best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]