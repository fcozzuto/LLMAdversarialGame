def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if resources:
        # Strategy: deny by prioritizing resources where we become strictly closer than opponent,
        # else move toward the best "lead" while avoiding moves that bring us closer to opponent's lead.
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue

            self_step = 0
            opp_step_pen = 0
            for rx, ry in resources:
                self_d_now = dist(sx, sy, rx, ry)
                opp_d_now = dist(ox, oy, rx, ry)
                self_d_next = dist(nx, ny, rx, ry)
                opp_d_next = dist(ox + (0 if ox == ox else 0), oy + 0, rx, ry)  # opponent assumed non-move for score baseline
                # Lead improvement using only our next position (deterministic, robust to unknown opponent move)
                lead_now = opp_d_now - self_d_now
                lead_next = opp_d_now - self_d_next

                # Prefer capturing/landing on resources immediately
                capture_bonus = 1000 if (nx == rx and ny == ry) else 0

                # If we create or increase a lead, reward; if we reduce our lead, penalize.
                self_step += capture_bonus + (lead_next - lead_now) * 3 + lead_next * 0.6

                # Penalize moves that make us simultaneously close to resources where opponent is already very close
                # (to resist "resource_denier" interference).
                if lead_now < 0:
                    opp_step_pen += (-lead_now) * 0.15

            val = self_step - opp_step_pen
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
        return best_move

    # No resources visible: move toward a corner that maximizes distance from opponent, but keep safe from obstacles.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target = max(corners, key=lambda c: dist(c[0], c[1], ox, oy) - dist(sx, sy, c[0], c[1]))
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        v = -dist(nx, ny, target[0], target[1]) + 0.05 * dist(nx, ny, ox, oy)
        if v > best_val:
            best_val = v
            best_move = [dx, dy]
    return best_move