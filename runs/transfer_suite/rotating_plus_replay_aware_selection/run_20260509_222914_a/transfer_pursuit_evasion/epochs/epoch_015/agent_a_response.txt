def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(nx, ny): return 0 <= nx < w and 0 <= ny < h
    def free(nx, ny): return inb(nx, ny) and (nx, ny) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("purs" in self_role) or ("catch" in self_role) or ("hunter" in self_role)

    # Targets: for pursuer, bias toward edges/corners; for evader, bias away from opponent.
    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]
    if pursuer:
        # Prefer corner that is farthest from us? Actually to trap, aim toward opponent's nearer side via opponent-centered corner.
        target = max(corners, key=lambda c: cheb(c[0], c[1], x, y))
        obj = "min"  # we'll minimize score below
    else:
        target = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        obj = "max"

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not free(nx, ny):
            continue

        d_opp = cheb(nx, ny, ox, oy)
        d_tgt = cheb(nx, ny, target[0], target[1])

        # Obstacle repulsion: stay away from close blocks.
        obs_cost = 0
        for ax, ay in obstacles:
            dist = cheb(nx, ny, ax, ay)
            if dist == 0:
                obs_cost += 1000
            elif dist == 1:
                obs_cost += 12
            elif dist == 2:
                obs_cost += 4

        # Additional structure:
        # - pursuer: reduce distance to opponent and drift toward target
        # - evader: increase distance from opponent and head to target
        if pursuer:
            score = (d_opp * -1) + (-0.5 * d_tgt) - obs_cost
        else:
            score = (d_opp * 1) + (0.4 * d_tgt) - obs_cost

        if best_score is None or (score > best_score if obj == "max" else score < best_score):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]