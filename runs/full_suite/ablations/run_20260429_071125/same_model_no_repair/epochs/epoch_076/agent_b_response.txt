def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    ox, oy = observation["opponent_position"]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Prefer diagonal but keep movement legal.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Select move that improves our advantage for capturing some resource.
    best_move = None
    best_val = None
    # Tie-break deterministically by move order in deltas list.
    for dx, dy, nx, ny in legal:
        move_val = -10**9
        for rx, ry in resources:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Higher is better: prioritize resources where we are closer after the move.
            # Small bias toward nearer resources overall to finish faster.
            val = (opp_d - our_d) * 100 - our_d
            if val > move_val:
                move_val = val
        # Additional deterministic bias: move away from opponent slightly when tied.
        opp_curr = cheb(sx, sy, ox, oy)
        opp_next = cheb(nx, ny, ox, oy)
        move_val += (opp_next - opp_curr)
        if best_val is None or move_val > best_val:
            best_val = move_val
            best_move = [dx, dy]
    return best_move